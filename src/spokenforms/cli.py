from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Literal
from uuid import uuid4

import typer

from spokenforms.config import apply_cli_overrides, load_config, write_default_config
from spokenforms.entities.builtins import built_in_entities
from spokenforms.generation import run_pipeline
from spokenforms.models import ProviderName, SensitiveType
from spokenforms.providers import create_provider
from spokenforms.stats import compute_stats, render_stats_markdown
from spokenforms.storage.exporters import export_csv, export_parquet
from spokenforms.storage.jsonl import write_jsonl
from spokenforms.storage.manifest import build_manifest, write_json
from spokenforms.utils.paths import ensure_dir

app = typer.Typer(help="Generate synthetic spoken transcript datasets.")


@app.command()
def init(output: Annotated[Path, typer.Option("--output", "-o")] = Path()) -> None:
    ensure_dir(output)
    write_default_config(output / "config.yaml")
    examples = output / "examples"
    ensure_dir(examples)
    entities = [entity.model_dump(mode="json") for entity in built_in_entities()]
    write_json(examples / "entities.json", entities)
    typer.echo(f"Initialized SpokenForms project at {output}")


@app.command()
def build(
    config: Annotated[Path | None, typer.Option("--config", "-c")] = None,
    entity: Annotated[str, typer.Option("--entity")] = "",
    num_values: Annotated[int | None, typer.Option("--num-values")] = None,
    target_per_pattern: Annotated[int | None, typer.Option("--target-per-pattern")] = None,
    provider: Annotated[ProviderName | None, typer.Option("--provider")] = None,
    output_dir: Annotated[Path | None, typer.Option("--output-dir")] = None,
    allow_potentially_real_sensitive_values: Annotated[
        bool,
        typer.Option("--allow-potentially-real-sensitive-values"),
    ] = False,
    i_understand_sensitive_data_risk: Annotated[
        bool,
        typer.Option("--i-understand-sensitive-data-risk"),
    ] = False,
) -> None:
    if allow_potentially_real_sensitive_values or i_understand_sensitive_data_risk:
        typer.echo("Unsafe sensitive-value generation is not implemented for v0.1.", err=True)
        raise typer.Exit(2)

    resolved = apply_cli_overrides(
        load_config(config),
        provider=provider,
        num_values=num_values,
        target_per_pattern=target_per_pattern,
        output_dir=output_dir,
    )
    run_id = str(uuid4())
    started = datetime.now(UTC)
    run_dir = ensure_dir(resolved.project.output_dir)
    llm_provider = create_provider(resolved.llm.provider, resolved.llm.model)
    result = run_pipeline(run_id=run_id, entity_id=entity, config=resolved, provider=llm_provider)
    stats = compute_stats(result.records, result.pair_statuses)
    sensitive_types: list[SensitiveType] = sorted(
        {
            record.sensitive_policy.sensitive_type
            for record in result.records
            if record.sensitive_policy.sensitive_type is not SensitiveType.NONE
        }
    )
    status: Literal["completed", "completed_with_underfilled_pairs"] = (
        "completed"
        if all(pair.status == "complete" for pair in result.pair_statuses)
        else "completed_with_underfilled_pairs"
    )
    manifest = build_manifest(
        run_id=run_id,
        created_at=started,
        updated_at=datetime.now(UTC),
        config=resolved,
        provider=llm_provider.name,
        model=llm_provider.model,
        entities=[entity],
        sensitive_types=sensitive_types,
        status=status,
    )

    write_json(run_dir / "manifest.json", manifest)
    write_json(run_dir / "config.resolved.yaml", resolved)
    write_jsonl(run_dir / "values.jsonl", result.values)
    write_jsonl(run_dir / "candidates.jsonl", result.records)
    write_jsonl(run_dir / "validated.jsonl", result.records)
    write_jsonl(run_dir / "dataset.jsonl", result.records)
    export_csv(run_dir / "dataset.csv", result.records)
    export_parquet(run_dir / "dataset.parquet", result.records)
    write_json(run_dir / "stats.json", stats)
    (run_dir / "stats.md").write_text(render_stats_markdown(stats), encoding="utf-8")
    (run_dir / "logs.jsonl").write_text("", encoding="utf-8")
    typer.echo(f"Wrote {len(result.records)} records to {run_dir}")


@app.command()
def stats(dataset: Annotated[Path, typer.Argument()]) -> None:
    from spokenforms.storage.jsonl import read_jsonl

    rows = read_jsonl(dataset)
    typer.echo(f"records: {len(rows)}")

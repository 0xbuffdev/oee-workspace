# Assessment evidence in your workspace

You can use OEE Workspace to record what you submitted for each assessment attempt, the work it refers to and any evaluation you received. The [OEE Evidence Rules](https://github.com/0xbuffdev/open-engineering-education/blob/main/spec/evidence-rules.md) determine what evidence is required.

Workspace records attempts. It does not grade them, establish achievement or issue certificates.

## Record format

The active format is [assessment-attempt schema v2](schemas/attempt-v2.schema.json). Each record has a UUIDv4, UTC timestamp, exact OEE release and course identity, one required assessment ID and its outcome references. Optional fields describe artifacts, observations, assistance and evaluation.

New attempts start with an empty artifacts list, an empty observations list and a null evaluation. An evaluation may be self-reported or attributed to a reviewer; the CLI does not authenticate that identity.

References to files inside your Workspace are relative paths. You can include SHA-256 hashes to detect changed bytes. External HTTP(S) references are display-only and are never fetched. Do not point a local artifact outside the learner directory or include private credentials.

## Create, check and export

After [installing the signed curriculum](../docs/CLI-SETUP.md), run from your Workspace root:

```sh
python -m oee_workspace evidence init --course SEF1 --assessment SEF1-AS1 --dest .
```

The command prints the new attempt file, such as `evidence/SEF/SEF1/SEF1-AS1/ATTEMPT-UUID.json`. Open it, keep the canonical identifiers unchanged and add links to files you actually created. Replace the UUID placeholder in the following commands:

```sh
python -m oee_workspace evidence check --path evidence/SEF/SEF1/SEF1-AS1/ATTEMPT-UUID.json --dest .
python -m oee_workspace status --course SEF1 --dest .
python -m oee_workspace export --dest . --attempt ATTEMPT-UUID --output exports/selected.json
```

The validator checks record shape, release identity, required assessment references and local artifact paths and hashes. Missing files, incorrect hashes and invalid source references fail the check. It does not execute your programs.

`status` shows locally recorded attempts and evaluation decisions. `export` writes only the selected JSON records to a new local file; it never includes the referenced artifact bytes or overwrites an existing output file. Share supporting work separately when required.

Use the default project `oee-curriculum.lock.json` from the working directory, or select a reviewed `--lock` and already verified `--store` explicitly. An absent release cannot be replaced with a Git checkout or automatically fetched.

## Privacy and assessment claims

Keep work you do not want public in a private repository. Review exports and attached files before sending them to an assessor. A structural check or a reviewer name written in JSON does not prove that the course was completed.

The CLI preserves existing learner work. It does not repin evidence, convert attempt formats, revise old assessments, upload records or make academic decisions on your behalf.

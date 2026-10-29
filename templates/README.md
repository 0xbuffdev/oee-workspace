# Workspace templates

This directory holds the templates used by the workspace generation scripts. Generated files are starting points for your own work; they are not canonical course definitions.

## Template directories

| Path | Purpose |
| --- | --- |
| `course-workspace/` | Files created for a course's labs, exercises, and notes |
| `project-workspace/` | Files created for a project: design, evaluation, retrospective, and (where required) authorization |
| `progress.md` | A general progress and evidence-log template |

The generation scripts in [`../scripts/`](../scripts/) use these files to create a consistent workspace structure.

## Relationship to OEE

The canonical specification, curriculum, course requirements, and project briefs stay in the [OEE repository](https://github.com/0xbuffdev/open-engineering-education).

Templates may link to canonical OEE documents, but they must not become competing sources of course requirements.

## Generated files are independent copies

A generated workspace is a snapshot of its template at the time of generation. Changing a template does not update files that were generated earlier.

When improving a template:

1. Make the change here.
2. Run the generator against a clean workspace.
3. Confirm the generated file contains the expected links and content.
4. Confirm the generator does not overwrite existing learner files.
5. Update the documentation if the generated layout or behavior changes.

## Learner ownership

Copy templates into your own workspace and customize them there. Commit learner work to your own workspace repository, not to the upstream starter repository.

Never include credentials, secrets, or private learner data in a template.

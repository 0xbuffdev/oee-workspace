<!-- markdownlint-disable MD041 -->
<img width="1800" height="298" alt="OEE Workspace banner" src="https://github.com/user-attachments/assets/137ba418-0429-418e-8e71-917bd008577f" />

# OEE Workspace

OEE Workspace is a free place to study software engineering and keep the work you produce along the way. Use it with the [Open Engineering Education (OEE) curriculum](https://github.com/0xbuffdev/open-engineering-education), whether you're learning your first programming concepts or developing skills in a new engineering field.

OEE provides the courses, lessons and assessments. Your Workspace holds your notes, code, experiments, projects and progress. You can start with just a folder and a text editor. No account, paid book or command-line setup is required to study.

## Get started

### 1. Choose what to learn

Browse the [OEE curriculum](https://github.com/0xbuffdev/open-engineering-education/tree/f2afed3e36f6ae0495e2b44a8d9337661defeda1/curriculum) and pick a course that fits your current experience.

- **Starting out?** Begin with [SEF1: Demystifying the Computer System](https://github.com/0xbuffdev/open-engineering-education/blob/f2afed3e36f6ae0495e2b44a8d9337661defeda1/curriculum/SEF/SEF1.md) and follow the [Foundations study order](https://github.com/0xbuffdev/open-engineering-education/blob/f2afed3e36f6ae0495e2b44a8d9337661defeda1/curriculum/SEF/README.md).
- **Already an engineer?** Choose a course from [Application Engineering](https://github.com/0xbuffdev/open-engineering-education/tree/f2afed3e36f6ae0495e2b44a8d9337661defeda1/curriculum/APP), [Systems Engineering](https://github.com/0xbuffdev/open-engineering-education/tree/f2afed3e36f6ae0495e2b44a8d9337661defeda1/curriculum/SYS), [AI Engineering](https://github.com/0xbuffdev/open-engineering-education/tree/f2afed3e36f6ae0495e2b44a8d9337661defeda1/curriculum/AI), or [Security Engineering](https://github.com/0xbuffdev/open-engineering-education/tree/f2afed3e36f6ae0495e2b44a8d9337661defeda1/curriculum/SEC). Check the course's prerequisites before starting.

These links point to the curriculum release selected by this Workspace. You can browse the latest curriculum separately, but use the selected release for lessons and assessment evidence.

### 2. Make your own Workspace

On the [OEE Workspace repository](https://github.com/0xbuffdev/oee-workspace), select **Use this template**, then **Create a new repository**. Give it a name and choose **Private** if your work, notes or assessment evidence should stay personal.

If you don't use GitHub repositories, select **Code → Download ZIP** instead. Extract the ZIP to a folder on your computer.

### 3. Open it locally

If you created a repository on GitHub, copy its URL and clone it:

```sh
git clone https://github.com/YOUR-USERNAME/YOUR-WORKSPACE.git
cd YOUR-WORKSPACE
```

Replace `YOUR-USERNAME` and `YOUR-WORKSPACE` with your repository details. You need [Git](https://git-scm.com/) for this option.

If you downloaded a ZIP, open the extracted folder instead. Open your Workspace in VS Code or any editor that can work with Markdown files.

### 4. Begin your course

Open the course you chose in the [OEE curriculum](https://github.com/0xbuffdev/open-engineering-education/tree/f2afed3e36f6ae0495e2b44a8d9337661defeda1/curriculum). Read its outcomes and required assessments, then work through the lessons and activities in the course's prescribed order.

Keep what you produce in your Workspace:

| Where | What goes there |
| --- | --- |
| [`progress.md`](progress.md) | Your current course, completed work and next steps |
| [`notes/`](notes/README.md) | Explanations, questions and useful references |
| [`labs/`](labs/README.md) | Experiments, observations and results |
| [`exercises/`](exercises/README.md) | Solutions, reasoning and tests |
| [`projects/`](projects/README.md) | Designs, implementations and evaluations |
| [`resources/`](resources/README.md) | Optional books and free learning materials |
| [`evidence/`](evidence/README.md) | Records of work submitted for course assessments |

You can create folders and Markdown files yourself. For example, start a `study/SEF1/` folder and write down what you understood from the first lesson. Link your work from `progress.md` as you go.

When an assessment asks you to build, explain or demonstrate something, save the actual work and how you tested it. The course tells you what counts as completion.

## Want the Workspace to organize course folders for you?

The optional Python CLI creates course folders using the OEE curriculum. It requires Python 3.11 and a one-time setup. Follow the [CLI setup guide](docs/CLI-SETUP.md), then run these commands from your Workspace folder:

```sh
python -m oee_workspace doctor
python -m oee_workspace course add SEF1 --dest .
```

Replace `SEF1` with the code of the course you selected. The first command checks your setup. The second creates folders for that course under `labs/`, `exercises/` and `notes/`. Project courses also get a folder under `projects/`.

The CLI leaves existing files alone. If you expect to use it later, keep your handwritten course work in a separate folder, such as `study/SEF1/`, until you've created the course folders.

## Track your progress and assessments

Update [`progress.md`](progress.md) as you study. Note what you finished, link your code or experiments, and record what you still need to work on.

If you installed the CLI, you can create an assessment record after completing the relevant work. For example, for the first SEF1 assessment:

```sh
python -m oee_workspace evidence init --course SEF1 --assessment SEF1-AS1 --dest .
python -m oee_workspace status --course SEF1 --dest .
```

Open the new record and add references to your actual work. The [evidence guide](evidence/README.md) explains how to check and share records. Workspace helps you organize evidence; it does not grade work or award certificates.

## Need help?

If a command fails or the Workspace behaves unexpectedly, [open an issue](https://github.com/0xbuffdev/oee-workspace/issues). Don't include passwords, private files or personal assessment records.

Want to improve the Workspace itself? See [CONTRIBUTING.md](CONTRIBUTING.md). Changes to OEE lessons and assessment requirements belong in the [OEE curriculum repository](https://github.com/0xbuffdev/open-engineering-education).

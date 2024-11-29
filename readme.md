# C-LARA Documentation

## 1. Purpose of C-LARA

C-LARA is a complete reimplementation of the Learning And Reading Assistant (LARA) [original LARA project](https://www.unige.ch/callector/lara/), with ChatGPT-4 at its core. 

### Key Features
- Provides a web platform to create and read multimedia learner texts in various languages.
- Automates many tasks that were manual in the original LARA, including text creation.
- Enables native speakers to quickly correct minor errors using an editing interface.

### Requirements
- **OpenAI API Key:** A license key with GPT-4 access is mandatory.
- GPT-3.5-turbo is insufficient for the multilingual processing tasks required.

---

## 2. Installation

C-LARA can be installed in two configurations:
1. **Local Machine**  
2. **Heroku (requires Postgres + S3)**

### 2a. Python and Packages
1. Install **Python 3.11**.  
   *Important:* Versions earlier than 3.11, such as 3.9, are not supported.
2. Install the required Python packages listed in `requirements.txt`.

### 2b. Downloading the Code
Clone the repository from GitHub:
```bash
git clone https://github.com/mannyrayner/C-LARA
```

### 2c. TreeTagger
Install TreeTagger for tagging/lemmatization:
- Follow instructions at [TreeTagger Installation Guide](https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/).
- Download parameter files for your desired languages.

### 2d. Environment Variables
Set the following environment variables:

| Variable                 | Description                                                  |
|--------------------------|--------------------------------------------------------------|
| `OPENAI_API_KEY`         | Value of your OpenAI GPT-4 license key.                      |
| `CLARA_ENVIRONMENT`      | Set to `local` (local machine) or `heroku` (Heroku).         |
| `CLARA`                  | Root directory of the cloned repository.                    |
| `FILE_STORAGE_TYPE`      | `local` for filesystem storage, `S3` for AWS S3 files.       |
| `AWS_ACCESS_KEY`         | AWS access key for S3 storage.                               |
| `AWS_REGION`             | AWS region name.                                             |
| `AWS_S3_REGION_NAME`     | AWS S3 region name.                                          |
| `AWS_SECRET_ACCESS_KEY`  | AWS secret access key.                                       |
| `S3_BUCKET_NAME`         | Name of your S3 bucket.                                      |
| `DB_TYPE`                | `postgres` or `sqlite` for database choice.                 |
| `DJANGO_DEBUG`           | `True` to enable Django debugging mode.                     |
| `GOOGLE_CREDENTIALS_JSON`| JSON configuration for Google TTS (optional).               |
| `TREETAGGER`             | Root directory of TreeTagger installation.                  |
| `TMPDIR`                 | On Heroku, set to `/tmp`.                                    |

### 2e. Installing on Heroku
1. Specify a Python 3 project on Heroku.
2. Set the environment variables as described above.
3. Link the GitHub repository.
4. Allocate resources for the processes listed in `Procfile`:

| Process                   | Resources       |
|---------------------------|-----------------|
| `gunicorn clara_project.wsgi:application` | Standard 1X dynos |
| `python manage.py qcluster`              | Standard 2X dynos |

5. Use Heroku Postgres (Standard 0 tier).

---

## 3. Running in Development Mode on a Local Machine

1. Ensure packages are installed and environment variables are set as described in Section 2.
2. Open two command prompts:

### Command Prompt 1 (Q-cluster for Django-Q asynchrony)
```bash
cd $CLARA
python3 manage.py qcluster
```

### Command Prompt 2 (Server)
```bash
cd $CLARA
python3 manage.py runserver
```

3. Access C-LARA at [http://localhost:8000/accounts/login/](http://localhost:8000/accounts/login/).

> If you encounter issues, email the full trace to **Manny.Rayner@unisa.edu.au** for support.

---

## 4. Organisation of Material

### Directory Structure
- **`$CLARA`**: Root C-LARA directory, based on the `CLARA` environment variable.
- **Core Python Code**: `$CLARA/clara_app/clara_core`.
- **Django Layer**: `$CLARA/clara_app`.

### 4a. Core Python Code
#### Key Files
- `clara_main.py`: Top-level class `CLARAProjectInternal`, which manages project operations.
- `clara_classes.py`: Defines internal text representation classes.
- `clara_prompt_templates.py`: Manages language-specific prompt templates.

#### Supporting Files
- `clara_cefr.py`: Estimates CEFR reading level.
- `clara_chatgpt4.py`: Sends requests to GPT-4 via API.
- `clara_chinese.py`: Handles Chinese-specific processing with Jieba.
- `clara_correct_syntax.py`: Corrects malformed annotated text.
- `clara_create_annotations.py`: Adds segmentation, gloss, and lemma annotations.
- `clara_diff.py`: Compares versions of CLARA files.
- `clara_merge_glossed_and_tagged.py`: Combines glossed and lemma-tagged text objects.
- `clara_renderer.py`: Generates static HTML multimedia files.

#### Configuration and Utilities
- `config.ini`: Configuration file.
- `clara_utils.py`: Utility functions.

### 4b. Django Layer
#### Key Files
- **`views.py`**: Handles operations such as project creation, annotation, and rendering.
- **`urls.py`**: Maps URLs to operations.
- **`models.py`**: Defines SQLite3/Postgres database tables.
- **`forms.py`**: Defines forms for database interactions.

#### Templates and Static Files
- **Templates**: Located in `$CLARA/clara_app/templates/clara_app`.
- **CSS and JS**: Located in `$CLARA/static`.

### 4c. HTML Templates for Core Python Code
Located in `$CLARA/templates`:

| File                        | Purpose                                    |
|-----------------------------|--------------------------------------------|
| `alphabetical_vocabulary_list.html` | Alphabetical vocabulary list.         |
| `clara_page.html`           | Main C-LARA content page.                  |
| `concordance_page.html`     | Concordance page.                          |
| `frequency_vocabulary_list.html` | Frequency-ordered vocabulary list.     |

### 4d. CSS and JavaScript
Located in `$CLARA/static`:

| File             | Description                          |
|------------------|--------------------------------------|
| `clara_styles.css` | CSS for multimedia content.         |
| `clara_scripts.js` | JavaScript for multimedia content.  |

### 4e. Prompt Templates and Examples
Located in `$CLARA/prompt_templates`:

- Subdirectories for each language and a `default` directory for language-independent defaults.
- **Templates**: `.txt` files.
- **Examples**: `.json` files.

> **Code Reference**: `$CLARA/clara_app/clara_core/clara_prompt_templates.py` and `views.py` (`edit_prompt` view).
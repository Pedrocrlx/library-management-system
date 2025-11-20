# library-management-system

### 1. Install the vscode extension.
    - Dev Containers

---

### 2. Make sure that you are inside of devcontainer.

If you getting errors, or cant connect to devcontainer then run:

```bash
make clean
```

Should resolve cache/volumes problems.

---

### 3. Install the dependencies

```bash
    poetry install --no-root
```

if you get permissions errors after run this command:

```bash
sudo chown -R $USER /library-management-system/.venv/
```

---
### 4. Check the enviroment that you are.

Should look like the example below:

```bash 
(library-management-system-py3.12) vscode ➜ /workspaces/library-management-system (feat/django-setup)
```

If not, run:
 ```bash
poetry env activate
```

Will be displayed something like this on terminal:

```bash
/workspaces/library-management-system/.venv/bin/activate
```

Then you copy this path, click on bottom right button to change your enviroment.

Select ```Enter interpreter path```

Then paste the path there. 

Kill/close the terminal and open a new one.

---

#### 5. Make sure that you create your branch from dev

- Check your branches using: 

```bash
git branch
```
If you just clone the project must have just **main** branch.

```bash
*main
```

So, if you just have the **main** you need to pull the **dev branch** from remote:

```bash
git branch pull origin dev
```

```bash
git switch dev
```

After this you can create your **feature** branch **from dev**.

Example: 

```bash
git switch -c feature/list-books
```

### How to run the project ?

- make run

# CodeGenome
### A Mini Version Control System in C++

CodeGenome is a **console-based C++ Object-Oriented Programming course project** that demonstrates how a simplified version-control system can organize source files, preserve historical versions, compare changes and recover older code. It uses **fixed-size arrays, classes, inheritance and file handling**; it does **not** use STL containers such as `vector`, `map` or `list`.

> **Project status:** Core and extended features are implemented on the development branch. End-to-end runtime verification is still pending. This is an educational prototype, **not a replacement for Git**.

## Contents
1. [Why we created CodeGenome](#why-we-created-codegenome)
2. [Objectives and capabilities](#objectives-and-capabilities)
3. [Architecture and workflow](#architecture-and-workflow)
4. [Project structure and file responsibilities](#project-structure-and-file-responsibilities)
5. [Requirements](#requirements)
6. [Clone the repository](#clone-the-repository)
7. [Compile and run](#compile-and-run)
8. [Login and permissions](#login-and-permissions)
9. [How to operate CodeGenome](#how-to-operate-codegenome)
10. [Complete worked example](#complete-worked-example)
11. [Data storage and persistence](#data-storage-and-persistence)
12. [OOP concepts demonstrated](#oop-concepts-demonstrated)
13. [Troubleshooting VS Code and GCC](#troubleshooting-vs-code-and-gcc)
14. [Constraints and known limitations](#constraints-and-known-limitations)
15. [Testing checklist](#testing-checklist)

## Why we created CodeGenome

Students frequently modify source code while completing assignments and projects. A newer edit may accidentally overwrite a working solution; keeping files such as `final.cpp`, `final2.cpp`, and `final_latest.cpp` makes changes difficult to track. Full Git workflows can also be intimidating when learning programming fundamentals.

**CodeGenome addresses that learning problem** by presenting essential version-control ideas in a menu-driven application: repositories, source files, commits, history, comparison and restoration. It helps students understand the mechanics behind version tracking while applying C++ OOP concepts in a meaningful project.

### Problem statement

Develop a lightweight version-management application that enables users to create code repositories, manage files, record versions, inspect historical changes and recover earlier versions using C++ and persistent file storage.

## Objectives and capabilities

| Objective | Implementation |
|---|---|
| Organize projects | Create and list repositories |
| Manage code | Add, edit, delete and view source-file records |
| Track revisions | Save a snapshot with commit ID, author, message and timestamp |
| Explore history | List previous commits for a repository or file |
| Compare revisions | Show content stored in two commits of the same file |
| Recover work | Restore a selected committed version to the working file |
| Find information | Search repository names, filenames, file contents and commit metadata |
| Summarize activity | View counts of repositories, files, commits and contributors |
| Audit commits | Display a reverse-chronological commit timeline |
| Retain data | Reload repositories, working files and commit snapshots on restart |

## Architecture and workflow

```text
User login (Admin / Student / Collaborator)
                       |
                    main.cpp
                       |
             Repository selection
                       |
          Repository + SourceFile
                |             |
             Storage      VersionManager
                |             |
       Working file data   Commit snapshots
                |             |
                +------+------+----------------+
                       |                       |
               SearchEngine             HistoryManager
                       |
                   Statistics
```

The application stores **working copies** separately from **committed snapshots**. Editing a file updates its working content. Committing saves an independent snapshot; restoring copies historical content back into the working file.

## Project structure and file responsibilities

```text
CodeGenome/
├── main.cpp
├── user.h
├── user.cpp
├── repository.h
├── repository.cpp
├── commit.h
├── commit.cpp
├── Storage.h
├── Storage.cpp
├── VersionManager.h
├── VersionManager.cpp
├── SearchEngine.h
├── SearchEngine.cpp
├── Statistics.h
├── Statistics.cpp
├── HistoryManager.h
├── HistoryManager.cpp
├── README.md
└── .gitignore
```

| File | Responsibility |
|---|---|
| `main.cpp` | Program entry point, login, input handling, main and repository menus; connects modules |
| `user.h` | Declares `User`, `Admin`, `Student`, `Collaborator` |
| `user.cpp` | Implements credentials, roles, virtual functions and repository-creation permission |
| `repository.h` | Declares `SourceFile` and `Repository` classes |
| `repository.cpp` | Implements source-file creation, editing, deletion, lookup, listing and restoration |
| `commit.h` | Declares the original `Commit` class, static count and equality operator |
| `commit.cpp` | Implements original commit object, timestamp, text-file export and operator overloading |
| `Storage.h` | Declares persistence interface |
| `Storage.cpp` | Saves and loads repositories and their working source files; imports legacy repository names |
| `VersionManager.h` | Declares `VersionRecord` and snapshot/history/compare/restore operations |
| `VersionManager.cpp` | Saves persistent snapshots, assigns IDs, lists history, compares and restores versions |
| `SearchEngine.h/.cpp` | Searches project records without STL containers |
| `Statistics.h/.cpp` | Calculates repository, file, commit and contributor totals |
| `HistoryManager.h/.cpp` | Displays commit timeline, most recent first |
| `.gitignore` | Excludes executables, object files, local data and editor settings |
| `README.md` | Project documentation, setup and operating instructions |

**Important:** `Commit` is retained as part of the original OOP implementation. The currently integrated menu uses `VersionManager` for persistent commits.

## Requirements

- Windows 10/11 (instructions below use Windows CMD)
- Visual Studio Code
- C/C++ extension for VS Code (recommended)
- Git
- GCC / MinGW-w64 with `g++` supporting C++11

Check installations in the **VS Code Terminal**:

```bat
git --version
g++ --version
where g++
```

## Clone the repository

1. Open VS Code.
2. Open **Terminal > New Terminal** (or press `Ctrl+``).
3. Navigate to the directory in which you want the new project folder:

```bat
cd %USERPROFILE%\Documents
```

4. Clone the repository (GitHub authentication/access is required because it is private):

```bat
git clone https://github.com/nidaa1308-arch/CodeGenome.git
cd CodeGenome
```

5. The completed-feature implementation is on the development branch:

```bat
git fetch origin
git switch feat/complete-version-control
```

6. Open the folder in VS Code:

```bat
code .
```

**Already have the local project?** Do not clone into the same existing folder. In your existing `CODEGENOME` directory, use:

```bat
git switch feat/complete-version-control
git pull origin feat/complete-version-control
```

## Compile and run

From the project root, use **Terminal**, not the VS Code **Output** panel:

```bat
g++ -std=c++11 -Wall user.cpp repository.cpp commit.cpp Storage.cpp VersionManager.cpp SearchEngine.cpp Statistics.cpp HistoryManager.cpp main.cpp -o CodeGenome.exe
```

If compilation succeeds, start it with:

```bat
.\CodeGenome.exe
```

If Windows immediately returns to the prompt with no output, use the troubleshooting section below.

## Login and permissions

**Demo credentials (hardcoded for classroom use only):**

| Username | Password | Role |
|---|---|---|
| `admin` | `1234` | Admin |
| `student` | `1234` | Student |
| `collab` | `1234` | Collaborator |

The Admin and Student accounts may create repositories. The Collaborator account cannot create repositories. In the integrated workflow, **only the owner of a repository** may add/edit/delete files, commit, or restore versions. Other users may browse repositories, files and history.

This is simplified educational access control, not secure authentication.

## How to operate CodeGenome

### Main menu

After login, the application offers:

| Option | Action | How to use |
|---|---|---|
| `1` | Create repository | Enter a unique repository name |
| `2` | List repositories | See existing repositories and their owners |
| `3` | Open repository | Enter its displayed number |
| `4` | Search | Enter a search term |
| `5` | Statistics | View repository/file/commit/contributor counts |
| `6` | Activity timeline | See recent commits in reverse chronological order |
| `0` | Exit | Save working repository state and close |

### Repository menu

Choose main-menu option `3`, then select a repository:

| Option | Action | How to use |
|---|---|---|
| `1` | Add file | Enter a filename, e.g. `hello.cpp` |
| `2` | Edit file | Enter filename and new content on one line |
| `3` | Delete file | Enter filename to remove it from working state |
| `4` | List files | Display current files |
| `5` | Commit file | Enter filename and a descriptive message |
| `6` | Version history | Enter a filename, or leave blank for all commits in repository |
| `7` | Compare versions | Enter two commit IDs from the same repository and file |
| `8` | Restore version | Enter an existing commit ID to restore its content |
| `9` | View file | Enter filename to inspect current content |
| `0` | Back | Return to main menu |

### Understanding commit IDs

A commit ID identifies a saved snapshot. IDs are assigned by `VersionManager` and persist across application restarts. A commit captures **one file at a time**, not an entire repository.

### Comparing versions

Select repository menu `7`. Supply two IDs belonging to the **same file and repository**. The current implementation displays the full previous and new content with `-` and `+` prefixes; it is **not** a line-by-line diff algorithm.

### Restoring versions

Select repository menu `8`, then enter a commit ID. CodeGenome copies the saved content into the working file (and can recreate a deleted file if capacity allows). **Restoring does not automatically create a new commit**. To preserve the restoration as a new version, commit that file afterward.

## Complete worked example

This example demonstrates the full version-control cycle.

1. Log in as `admin` with password `1234`.
2. Main menu `1`: create repository `DemoProject`.
3. Main menu `3`: open `DemoProject`.
4. Repository menu `1`: add `hello.cpp`.
5. Repository menu `2`: edit `hello.cpp` with `cout << "Version 1";`.
6. Repository menu `5`: commit `hello.cpp` with message `Initial working version`.
7. Edit `hello.cpp` again, replacing content with `cout << "Version 2";`.
8. Commit again with message `Updated output`.
9. Repository menu `6`: view history; note both commit IDs.
10. Repository menu `7`: compare the two IDs.
11. Repository menu `8`: restore the first commit ID.
12. Repository menu `9`: inspect `hello.cpp` to confirm the earlier content returned.
13. Return to main menu and try `4` (search), `5` (statistics) and `6` (timeline).
14. Exit and reopen the application; confirm the repository, working file and commits remain.

## Data storage and persistence

Generated local data files (ignored by Git):

| File | Data |
|---|---|
| `codegenome_repos.dat` | Repository names, owners and current source-file contents |
| `codegenome_versions.dat` | Committed file snapshots, IDs, authors, messages and timestamps |
| `repositories.txt` | Legacy repository list from the initial project, imported if the new data file is missing |
| `commits.txt` | Legacy text output used by the original `Commit` class, not the current version-history database |

**Do not delete `.dat` files if you want to retain local work.** They are stored relative to the program's working directory and are not uploaded to GitHub.

## OOP concepts demonstrated

| Concept | Example |
|---|---|
| Classes and objects | `User`, `Repository`, `SourceFile`, `Commit` |
| Encapsulation | Private fields with public methods |
| Inheritance | `Admin`, `Student`, `Collaborator` derive from `User` |
| Runtime polymorphism | Virtual `showRole()` and `canCreateRepository()` |
| Constructors and destructors | Initialization of users, repositories and commits |
| Function overloading | Two `Repository::addFile()` overloads |
| Operator overloading | `Commit::operator==` |
| Static class member | `Commit::totalCommits` |
| Composition | Repository contains a fixed array of source files |
| File handling | `ifstream`, `ofstream`, binary records |
| Exception handling | Legacy commit implementation uses `runtime_error` |
| Modular programming | Separate headers and implementation files |

No STL containers are used. Standard library **headers and utilities** such as `iostream`, `fstream`, `cstring` and `limits` are used.

## Troubleshooting VS Code and GCC

### 1. Red underlines on `#include <iostream>`

Check `g++ --version` and `where g++`. In VS Code press **Ctrl+Shift+P** → **C/C++: Select IntelliSense Configuration** and select the correct `g++.exe`. Alternatively set the compiler path in **C/C++: Edit Configurations (UI)**. The compiler path previously used for this project is `C:\tmp\gcc\bin\g++.exe`; verify it exists on your machine.

### 2. `ISO C++ forbids converting a string constant to char*`

This warning occurs when a constructor takes `char*` but its default value is a string literal. The development branch now uses `const char[]` for those constructor inputs.

### 3. The executable compiles but prints nothing

Check its Windows exit code in CMD:

```bat
.\CodeGenome.exe
echo %errorlevel%
```

If you see `-1073741515` or `3221225781`, Windows may be missing a required runtime DLL. Try rebuilding:

```bat
g++ -std=c++11 -static -static-libgcc -static-libstdc++ user.cpp repository.cpp commit.cpp Storage.cpp VersionManager.cpp SearchEngine.cpp Statistics.cpp HistoryManager.cpp main.cpp -o CodeGenome.exe
.\CodeGenome.exe
echo %errorlevel%
```

If it still fails, provide the exact exit code. **Do not assume that every blank run is a DLL problem.** If the code is zero but no menu appears, investigate which executable is running and the program's startup behavior.

### 4. `undefined reference to WinMain` or `main`

Make sure `main.cpp` is included in the compile command, defines `int main()`, and the build is configured as a **console** application.

### 5. `undefined reference to ...` for project classes

Compile **all nine** `.cpp` files together using the full command above. Compiling only `main.cpp` will not link the other class implementations.

### 6. Program works in terminal but not with Run Code

Use **Terminal → New Terminal** and the manual `g++` command. Some VS Code runners show output in a panel that cannot accept interactive input.

### 7. New GitHub changes do not appear locally

```bat
git branch --show-current
git pull origin feat/complete-version-control
```

Check for uncommitted local changes before switching branches or pulling.

## Constraints and known limitations

- Maximum **20 repositories** and **20 source files per repository**.
- File names up to **49 characters**, file content up to **499 characters** per file, and up to **1000 loaded commits**.
- File editing currently accepts a **single line** of text, so it is not a full source-code editor.
- Each commit stores a snapshot of **one file**, not the complete repository.
- Comparison shows full old/new content, not a precise line-by-line or character-level diff.
- Timeline shows **commits**, not every file edit or deletion.
- Search is basic and case-sensitive.
- Login uses hardcoded demo accounts and plaintext passwords in the source.
- Binary data files are compiler/build dependent and are not a portable format.
- Git branches, remote synchronization, merge conflict resolution and distributed Git functionality are **outside this mini project's scope**.
- Features are implemented but final integrated runtime testing is still required.

## Testing checklist

- [ ] Compile all project files without errors
- [ ] Start the application and log in as each role
- [ ] Create a repository and reject a duplicate name
- [ ] Add, edit, view and delete a file
- [ ] Restart and verify working-file persistence
- [ ] Commit two different versions of one file
- [ ] View history and compare the two commits
- [ ] Restore an older commit and verify content
- [ ] Restart and verify commit IDs and history
- [ ] Search repositories, filenames and commit messages
- [ ] Verify statistics and activity timeline
- [ ] Verify unauthorized modifications are rejected
- [ ] Check invalid menu input, file limits and storage errors

---

**CodeGenome** is intended to demonstrate the principles of version management and practical object-oriented software design in a manageable C++ course project.

# CodeGenome - Mini Version Control System

Console-based C++ OOP course project using fixed-size arrays and binary file persistence. No STL containers.

## Features
- Admin, student and collaborator login (demo credentials)
- Repository creation and owner-based write permissions
- Source file add, edit, delete, display and persistence
- Persistent per-file commit snapshots with unique IDs and timestamps
- Commit history, content comparison, restore
- Search repositories, filenames, file content and commit metadata
- Statistics dashboard and chronological commit activity timeline

## Build (Windows MinGW / g++)
```bat
g++ -std=c++11 -Wall user.cpp repository.cpp commit.cpp Storage.cpp VersionManager.cpp SearchEngine.cpp Statistics.cpp HistoryManager.cpp main.cpp -o CodeGenome.exe
.\CodeGenome.exe
```

Use the integrated VS Code **Terminal**, not the Output pane.

## Demo logins
admin / 1234; student / 1234; collab / 1234

## Notes
- 20 repositories, 20 source files per repository, 499 characters per file, 1000 commits max.
- Edit content is entered on a single line; version comparison displays old and new full content (not a line-by-line diff).
- Only repository owners may change or commit files; other users may browse.
- Repository and source-file state: `codegenome_repos.dat`.
- Commit snapshots: `codegenome_versions.dat`.
- Older `repositories.txt` entries are imported on first run if the new data file is absent.
- Demo credentials are hardcoded and are **not production authentication**.
- The original `Commit` class is retained for demonstrating OOP concepts; the integrated workflow uses `VersionManager` for persistent snapshots.
- Activity timeline currently records commits, not every edit or deletion.
- Binary storage is intended for the same compiler/build and is not a portable interchange format.

## Quick manual test
1. Log in as admin and create Demo.
2. Open Demo; add hello.cpp; edit content to version one; commit it.
3. Edit to version two; commit again.
4. View history; compare the two commit IDs; restore the first.
5. Exit, restart and verify repository, file content, and commit history persist.
6. Try search, statistics and timeline.

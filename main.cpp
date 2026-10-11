#include <iostream>
#include <cstring>
#include <limits>
#include "User.h"
#include "Repository.h"
#include "Storage.h"
#include "VersionManager.h"
#include "SearchEngine.h"
#include "Statistics.h"
#include "HistoryManager.h"
using namespace std;
Repository repositories[20];
int repositoryCount = 0;
VersionManager versions;
void clearLine() { cin.ignore(numeric_limits<streamsize>::max(), '\n'); }
int readNumber()
{
    int value;
    if(!(cin >> value)) { cin.clear(); clearLine(); return -1; }
    clearLine();
    return value;
}
void save()
{
    if(!Storage::saveRepositories(repositories, repositoryCount))
        cout << "\nWarning: could not save repositories.\n";
}
void showRepositories()
{
    cout << "\n========== REPOSITORIES ==========\n";
    for(int i = 0; i < repositoryCount; i++)
        cout << i + 1 << ". " << repositories[i].getRepoName() << " | Owner: " << repositories[i].getOwner() << endl;
    if(repositoryCount == 0) cout << "No repositories.\n";
}
void createRepository(User* user)
{
    if(!user->canCreateRepository()) { cout << "\nPermission denied.\n"; return; }
    if(repositoryCount >= 20) { cout << "\nRepository limit reached.\n"; return; }
    char name[50];
    cout << "Repository name: "; cin.getline(name, sizeof(name));
    if(!name[0]) return;
    for(int i = 0; i < repositoryCount; i++)
        if(strcmp(repositories[i].getRepoName(), name) == 0) { cout << "Already exists.\n"; return; }
    repositories[repositoryCount++] = Repository(name, user->getUsername());
    save();
    cout << "Repository created.\n";
}
void repositoryMenu(User* user)
{
    showRepositories();
    cout << "Repository number: ";
    int index = readNumber() - 1;
    if(index < 0 || index >= repositoryCount) { cout << "Invalid repository.\n"; return; }
    Repository& repo = repositories[index];
    bool canEdit = strcmp(repo.getOwner(), user->getUsername()) == 0;
    // Collaborators can view but cannot modify repositories they do not own.
    int choice;
    do
    {
        cout << "\n========== " << repo.getRepoName() << " ==========\n";
        cout << "1. Add file\n2. Edit file\n3. Delete file\n4. List files\n5. Commit file\n6. Version history\n7. Compare versions\n8. Restore version\n9. View file\n0. Back\nChoice: ";
        choice = readNumber();
        char name[50], content[500], message[100];
        SourceFile* file = 0;
        if(choice == 0) break;
        if((choice == 1 || choice == 2 || choice == 3 || choice == 5 || choice == 8) && !canEdit)
        { cout << "Only the repository owner can modify it.\n"; continue; }
        switch(choice)
        {
        case 1:
            cout << "File name: "; cin.getline(name, sizeof(name));
            if(!name[0]) break;
            repo.addFile(name); save(); break;
        case 2:
            cout << "File name: "; cin.getline(name, sizeof(name));
            file = repo.findFile(name);
            if(!file) { cout << "File not found.\n"; break; }
            cout << "New content (one line): "; cin.getline(content, sizeof(content));
            file->editFile(content); save(); cout << "Updated.\n"; break;
        case 3:
            cout << "File name: "; cin.getline(name, sizeof(name));
            repo.deleteFile(name); save(); break;
        case 4: repo.showFiles(); break;
        case 5:
            cout << "File name: "; cin.getline(name, sizeof(name));
            file = repo.findFile(name);
            if(!file) { cout << "File not found.\n"; break; }
            cout << "Commit message: "; cin.getline(message, sizeof(message));
            if(versions.commit(repo.getRepoName(), name, user->getUsername(), message, file->getContent()))
                cout << "Commit saved.\n";
            else cout << "Could not save commit.\n";
            break;
        case 6:
            cout << "Filter by file (blank for all): "; cin.getline(name, sizeof(name));
            versions.history(repo.getRepoName(), name); break;
        case 7:
        {
            cout << "First commit ID: "; int a = readNumber();
            cout << "Second commit ID: "; int b = readNumber();
            const VersionRecord* va = versions.get(a);
            if(!va || strcmp(va->repository, repo.getRepoName()) != 0 || !versions.compare(a, b))
                cout << "Both commits must exist in this repository and refer to the same file.\n";
            break;
        }
        case 8:
        {
            cout << "Commit ID to restore: "; int id = readNumber();
            if(versions.restore(repo, id)) { save(); cout << "Version restored to working file. Commit again to record restoration.\n"; }
            else cout << "Cannot restore this commit.\n";
            break;
        }
        case 9:
            cout << "File name: "; cin.getline(name, sizeof(name));
            file = repo.findFile(name);
            if(file) file->showFile(); else cout << "File not found.\n";
            break;
        default: cout << "Invalid choice.\n";
        }
    } while(choice != 0);
}
int main()
{
    repositoryCount = Storage::loadRepositories(repositories, 20);
    char adminName[] = "admin", studentName[] = "student", collabName[] = "collab", pass[] = "1234";
    Admin admin(adminName, pass);
    Student student(studentName, pass);
    Collaborator collab(collabName, pass);
    User* current = 0;
    char username[30], password[30];
    cout << "====================================\n        CODEGENOME\n Mini Version Control System\n====================================\nUsername: ";
    cin.getline(username, sizeof(username));
    cout << "Password: "; cin.getline(password, sizeof(password));
    if(admin.login(username, password)) current = &admin;
    else if(student.login(username, password)) current = &student;
    else if(collab.login(username, password)) current = &collab;
    if(!current) { cout << "Invalid login.\n"; return 1; }
    cout << "Welcome, " << current->getUsername() << " (";
    current->showRole(); cout << ")\n";
    int choice;
    do
    {
        cout << "\n========== MAIN MENU ==========\n1. Create repository\n2. List repositories\n3. Open repository\n4. Search\n5. Statistics\n6. Activity timeline\n0. Exit\nChoice: ";
        choice = readNumber();
        switch(choice)
        {
        case 1: createRepository(current); break;
        case 2: showRepositories(); break;
        case 3: repositoryMenu(current); break;
        case 4:
        {
            char term[100]; cout << "Search term: "; cin.getline(term, sizeof(term));
            if(term[0]) SearchEngine::search(repositories, repositoryCount, versions, term);
            break;
        }
        case 5: Statistics::show(repositories, repositoryCount, versions); break;
        case 6: HistoryManager::timeline(versions); break;
        case 0: save(); cout << "Goodbye.\n"; break;
        default: cout << "Invalid choice.\n";
        }
    } while(choice != 0);
    return 0;
}

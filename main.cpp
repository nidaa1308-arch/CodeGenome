#include <iostream>
#include <fstream>
#include <cstring>
#include <stdexcept>
#include "User.h"
#include "Repository.h"
#include "Commit.h"
#include "Storage.h"
using namespace std;
Repository repositories[20];
int repositoryCount = 0;
void saveRepository(Repository repo)
{
    ofstream file("repositories.txt", ios::app);
    if(!file)
        throw runtime_error("Unable to open repositories.txt");
    file << "Repository: " << repo.getRepoName() << endl;
    file << "Owner: " << repo.getOwner() << endl;
    file << "--------------------------" << endl;
    file.close();
}
void createRepository(User* user)
{
    char name[50];
    if(!user->canCreateRepository())
    {
        cout << "\nYou do not have permission to create a repository.";
        return;
    }
    cout << "\nEnter repository name: ";
    cin >> name;
    int i;
    for(i = 0; i < repositoryCount; i++)
    {
        if(strcmp(repositories[i].getRepoName(), name) == 0)
            throw runtime_error("Repository already exists.");
    }
    if(repositoryCount >= 20)
        throw runtime_error("Repository limit reached.");
    Repository repo(name, user->getUsername());
    repositories[repositoryCount] = repo;
    repositoryCount++;
    saveRepository(repo);
    cout << "\nRepository created successfully.";
}
void showRepositories()
{
    int i;
    cout << "\n\n========== REPOSITORIES ==========\n";
    if(repositoryCount == 0)
    {
        cout << "No repositories found.";
        return;
    }
    for(i = 0; i < repositoryCount; i++)
        cout << i + 1 << ". " << repositories[i].getRepoName() << " | Owner: " << repositories[i].getOwner() << endl;
}
void repositoryMenu(User* user)
{
    int choice,repoChoice;
    char fileName[50],content[500],message[100];
    if(repositoryCount == 0)
    {
        cout << "\nCreate a repository first.";
        return;
    }
    showRepositories();
    cout << "\nSelect repository: ";
    cin >> repoChoice;
    if(repoChoice < 1 || repoChoice > repositoryCount)
        throw runtime_error("Invalid repository number.");
    Repository& repo = repositories[repoChoice - 1];
    do
    {
        cout << "\n\n========== REPOSITORY MENU ==========";
        cout << "\n1. Add File";
        cout << "\n2. Edit File";
        cout << "\n3. Delete File";
        cout << "\n4. Show Files";
        cout << "\n5. Commit";
        cout << "\n6. Back";
        cout << "\nEnter choice: ";
        cin >> choice;
        switch(choice)
        {
        case 1:
            cout << "\nEnter file name: ";
            cin >> fileName;
            repo.addFile(fileName);
            break;
        case 2:
        {
            cout << "\nEnter file name: ";
            cin >> fileName;
            SourceFile* file = repo.findFile(fileName);
            if(file == 0)
                cout << "\nFile not found.";
            else
            {
                cout << "\nEnter new content: ";
                cin.ignore();
                cin.getline(content,500);
                file->editFile(content);
                cout << "\nFile updated successfully.";
            }
            break;
        }
        case 3:
            cout << "\nEnter file name: ";
            cin >> fileName;
            repo.deleteFile(fileName);
            break;
        case 4:
            repo.showFiles();
            break;
        case 5:
        {
            cout << "\nEnter file name: ";
            cin >> fileName;
            SourceFile* file = repo.findFile(fileName);
            if(file == 0)
                cout << "\nFile not found.";
            else
            {
                cout << "\nEnter commit message: ";
                cin.ignore();
                cin.getline(message,100);
                Commit commit(message,user->getUsername(),file->getFileName(),file->getContent());
                commit.saveToFile();
                cout << "\nCommit created successfully.";
                commit.showCommit();
            }
            break;
        }
        case 6:
            cout << "\nReturning to main menu.";
            break;
        default:
            cout << "\nInvalid choice.";
        }
    }while(choice != 6);
}
int main()
{
    repositoryCount = Storage::loadRepositories(repositories, 20);
    char adminUser[] = "admin",adminPass[] = "1234";
    char studentUser[] = "student",studentPass[] = "1234";
    char collabUser[] = "collab",collabPass[] = "1234";
    Admin admin(adminUser,adminPass);
    Student student(studentUser,studentPass);
    Collaborator collaborator(collabUser,collabPass);
    User* currentUser = 0;
    char username[30],password[30];
    cout << "====================================";
    cout << "\n        CODEGENOME";
    cout << "\n Mini Version Control System";
    cout << "\n====================================";
    cout << "\n\nUsername: ";
    cin >> username;
    cout << "Password: ";
    cin >> password;
    if(admin.login(username,password))
        currentUser = &admin;
    else if(student.login(username,password))
        currentUser = &student;
    else if(collaborator.login(username,password))
        currentUser = &collaborator;
    else
    {
        cout << "\nInvalid username or password.";
        return 0;
    }
    cout << "\n\nLogin successful!";
    cout << "\nRole: ";
    currentUser->showRole();
    int choice;
    do
    {
        try
        {
            cout << "\n\n========== MAIN MENU ==========";
            cout << "\n1. Create Repository";
            cout << "\n2. Show Repositories";
            cout << "\n3. Open Repository";
            cout << "\n4. Total Commits";
            cout << "\n5. Exit";
            cout << "\nEnter choice: ";
            cin >> choice;
            switch(choice)
            {
            case 1:
                createRepository(currentUser);
                break;
            case 2:
                showRepositories();
                break;
            case 3:
                repositoryMenu(currentUser);
                break;
            case 4:
                cout << "\nTotal Commits: " << Commit::getTotalCommits();
                break;
            case 5:
                cout << "\nThank you for using CodeGenome!";
                break;
            default:
                cout << "\nInvalid choice.";
            }
        }
        catch(exception& e)
        {
            cout << "\nError: " << e.what();
        }
    }while(choice != 5);
    return 0;
}
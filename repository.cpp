#include <iostream>
#include <cstring>
#include "Repository.h"
using namespace std;
SourceFile::SourceFile(char name[], char data[])
{
    strcpy(fileName, name);
    strcpy(content, data);
}
void SourceFile::editFile(char data[])
{
    strcpy(content, data);
}
char* SourceFile::getFileName()
{
    return fileName;
}
char* SourceFile::getContent()
{
    return content;
}
void SourceFile::showFile()
{
    cout << "\nFile Name: " << fileName;
    cout << "\nContent: " << content << endl;
}
Repository::Repository(char name[], char user[])
{
    strcpy(repoName, name);
    strcpy(owner, user);
    fileCount = 0;
}
void Repository::addFile(SourceFile file)
{
    if(fileCount < 20)
    {
        files[fileCount] = file;
        fileCount++;
        cout << "\nFile added successfully.";
    }
    else
        cout << "\nFile limit reached.";
}
void Repository::addFile(char fileName[])
{
    if(fileCount < 20)
    {
        SourceFile file(fileName);
        files[fileCount] = file;
        fileCount++;
        cout << "\nFile added successfully.";
    }
    else
        cout << "\nFile limit reached.";
}
SourceFile* Repository::findFile(char fileName[])
{
    int i;
    for(i = 0; i < fileCount; i++)
    {
        if(strcmp(files[i].getFileName(), fileName) == 0)
            return &files[i];
    }
    return 0;
}
void Repository::deleteFile(char fileName[])
{
    int i,j;
    for(i = 0; i < fileCount; i++)
    {
        if(strcmp(files[i].getFileName(), fileName) == 0)
        {
            for(j = i; j < fileCount - 1; j++)
                files[j] = files[j + 1];
            fileCount--;
            cout << "\nFile deleted successfully.";
            return;
        }
    }
    cout << "\nFile not found.";
}
void Repository::showFiles()
{
    int i;
    cout << "\nRepository: " << repoName << endl;
    if(fileCount == 0)
    {
        cout << "No files found.";
        return;
    }
    for(i = 0; i < fileCount; i++)
        cout << i + 1 << ". " << files[i].getFileName() << endl;
}
char* Repository::getRepoName()
{
    return repoName;
}
char* Repository::getOwner()
{
    return owner;
}
#include <iostream>
#include <cstring>
#include "Repository.h"
using namespace std;
SourceFile::SourceFile(const char name[], const char data[])
{
    strncpy(fileName, name, 49); fileName[49] = '\0';
    strncpy(content, data, 499); content[499] = '\0';
}
void SourceFile::editFile(const char data[])
{
    strncpy(content, data, 499); content[499] = '\0';
}
char* SourceFile::getFileName() { return fileName; }
char* SourceFile::getContent() { return content; }
void SourceFile::showFile() { cout << "\nFile: " << fileName << "\nContent: " << content << endl; }
Repository::Repository(const char name[], const char user[])
{
    strncpy(repoName, name, 49); repoName[49] = '\0';
    strncpy(owner, user, 29); owner[29] = '\0';
    fileCount = 0;
}
void Repository::addFile(SourceFile file)
{
    if(fileCount >= 20) { cout << "\nFile limit reached."; return; }
    if(findFile(file.getFileName())) { cout << "\nFile already exists."; return; }
    files[fileCount++] = file;
    cout << "\nFile added successfully.";
}
void Repository::addFile(const char fileName[]) { addFile(SourceFile(fileName)); }
bool Repository::restoreFile(const char fileName[], const char content[])
{
    SourceFile* existing = findFile(fileName);
    if(existing) { existing->editFile(content); return true; }
    if(fileCount >= 20) return false;
    files[fileCount++] = SourceFile(fileName, content);
    return true;
}
SourceFile* Repository::findFile(const char fileName[])
{
    for(int i = 0; i < fileCount; i++)
        if(strcmp(files[i].getFileName(), fileName) == 0) return &files[i];
    return 0;
}
void Repository::deleteFile(const char fileName[])
{
    for(int i = 0; i < fileCount; i++)
        if(strcmp(files[i].getFileName(), fileName) == 0)
        {
            for(int j = i; j < fileCount - 1; j++) files[j] = files[j + 1];
            fileCount--;
            cout << "\nFile deleted successfully.";
            return;
        }
    cout << "\nFile not found.";
}
void Repository::showFiles()
{
    cout << "\nRepository: " << repoName << " (" << fileCount << " files)\n";
    for(int i = 0; i < fileCount; i++) cout << i + 1 << ". " << files[i].getFileName() << endl;
}
char* Repository::getRepoName() { return repoName; }
char* Repository::getOwner() { return owner; }
int Repository::getFileCount() const { return fileCount; }
SourceFile* Repository::getFile(int index)
{
    return index >= 0 && index < fileCount ? &files[index] : 0;
}

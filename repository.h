#ifndef REPOSITORY_H
#define REPOSITORY_H
class SourceFile
{
private:
    char fileName[50];
    char content[500];
public:
    SourceFile(char name[] = "", char data[] = "");
    void editFile(char data[]);
    char* getFileName();
    char* getContent();
    void showFile();
};
class Repository
{
private:
    char repoName[50];
    char owner[30];
    SourceFile files[20];
    int fileCount;
public:
    Repository(char name[] = "", char user[] = "");
    void addFile(SourceFile file);
    void addFile(char fileName[]);
    SourceFile* findFile(char fileName[]);
    void deleteFile(char fileName[]);
    void showFiles();
    char* getRepoName();
    char* getOwner();
};
#endif
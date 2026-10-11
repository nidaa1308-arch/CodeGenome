#ifndef REPOSITORY_H
#define REPOSITORY_H
class SourceFile
{
private:
    char fileName[50];
    char content[500];
public:
    SourceFile(const char name[] = "", const char data[] = "");
    void editFile(const char data[]);
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
    Repository(const char name[] = "", const char user[] = "");
    void addFile(SourceFile file);
    void addFile(const char fileName[]);
    bool restoreFile(const char fileName[], const char content[]);
    SourceFile* findFile(const char fileName[]);
    void deleteFile(const char fileName[]);
    void showFiles();
    char* getRepoName();
    char* getOwner();
    int getFileCount() const;
    SourceFile* getFile(int index);
};
#endif

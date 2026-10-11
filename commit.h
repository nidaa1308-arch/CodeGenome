#ifndef COMMIT_H
#define COMMIT_H
class Commit
{
private:
    static int totalCommits;
    int commitID;
    char message[100];
    char author[30];
    char fileName[50];
    char content[500];
    char timeStamp[50];
public:
    Commit(const char msg[] = "", const char user[] = "", const char file[] = "", const char data[] = "");
    void showCommit();
    void saveToFile();
    static int getTotalCommits();
    bool operator==(const Commit& c);
};
#endif

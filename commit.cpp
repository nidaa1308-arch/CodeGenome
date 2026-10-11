#include <iostream>
#include <fstream>
#include <cstring>
#include <ctime>
#include <stdexcept>
#include "Commit.h"
using namespace std;
int Commit::totalCommits = 0;
Commit::Commit(const char msg[],const char user[],const char file[],const char data[])
{
    totalCommits++;
    commitID = totalCommits;
    strcpy(message, msg);
    strcpy(author, user);
    strcpy(fileName, file);
    strcpy(content, data);
    time_t now = time(0);
    strcpy(timeStamp, ctime(&now));
}
void Commit::showCommit()
{
    cout << "\n--------------------------";
    cout << "\nCommit ID: " << commitID;
    cout << "\nMessage: " << message;
    cout << "\nAuthor: " << author;
    cout << "Time: " << timeStamp;
    cout << "File: " << fileName;
    cout << "--------------------------";
}
void Commit::saveToFile()
{
    ofstream file("commits.txt", ios::app);
    if(!file)
        throw runtime_error("Unable to open commits.txt");
    file << "Commit ID: " << commitID << endl;
    file << "Message: " << message << endl;
    file << "Author: " << author << endl;
    file << "File: " << fileName << endl;
    file << "Content: " << content << endl;
    file << "Time: " << timeStamp;
    file << "--------------------------" << endl;
    file.close();
}
int Commit::getTotalCommits()
{
    return totalCommits;
}
bool Commit::operator==(const Commit& c)
{
    return commitID == c.commitID;
}
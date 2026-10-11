#include "SearchEngine.h"
#include <iostream>
#include <cstring>
using namespace std;
void SearchEngine::search(Repository repos[], int count, const VersionManager& versions, const char term[])
{
    int hits = 0;
    for(int i = 0; i < count; i++)
    {
        if(strstr(repos[i].getRepoName(), term))
        { cout << "\nRepository: " << repos[i].getRepoName(); hits++; }
        for(int j = 0; j < repos[i].getFileCount(); j++)
        {
            SourceFile* f = repos[i].getFile(j);
            if(strstr(f->getFileName(), term) || strstr(f->getContent(), term))
            { cout << "\nFile: " << repos[i].getRepoName() << "/" << f->getFileName(); hits++; }
        }
    }
    for(int i = 0; i < versions.total(); i++)
    {
        const VersionRecord* v = versions.at(i);
        if(strstr(v->message, term) || strstr(v->file, term) || strstr(v->author, term))
        { cout << "\nCommit #" << v->id << " " << v->repository << "/" << v->file << ": " << v->message; hits++; }
    }
    cout << "\nMatches: " << hits << endl;
}

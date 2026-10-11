#include "Statistics.h"
#include <iostream>
#include <cstring>
using namespace std;
void Statistics::show(Repository repos[], int count, const VersionManager& versions)
{
    int files = 0;
    cout << "\n========== STATISTICS ==========";
    for(int i = 0; i < count; i++) files += repos[i].getFileCount();
    cout << "\nRepositories: " << count << "\nSource files: " << files << "\nTotal commits: " << versions.total() << endl;
    for(int i = 0; i < count; i++)
        cout << repos[i].getRepoName() << " | files: " << repos[i].getFileCount() << " | commits: " << versions.countFor(repos[i].getRepoName()) << endl;
    char authors[1000][30] = {};
    int unique = 0;
    for(int i = 0; i < versions.total(); i++)
    {
        const VersionRecord* v = versions.at(i);
        bool exists = false;
        for(int j = 0; j < unique; j++) if(strcmp(authors[j], v->author) == 0) exists = true;
        if(!exists) { strncpy(authors[unique], v->author, 29); unique++; }
    }
    cout << "Commit contributors: " << unique << endl;
}

#include "HistoryManager.h"
#include <iostream>
using namespace std;
void HistoryManager::timeline(const VersionManager& versions)
{
    cout << "\n========== ACTIVITY TIMELINE ==========";
    for(int i = versions.total() - 1; i >= 0; i--)
    {
        const VersionRecord* v = versions.at(i);
        cout << "\n" << v->timestamp << " | " << v->author << " committed " << v->repository << "/" << v->file << " (#" << v->id << ")\n  " << v->message;
    }
    cout << endl;
}

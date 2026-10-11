#include "VersionManager.h"
#include <fstream>
#include <cstring>
#include <ctime>
#include <iostream>
using namespace std;
VersionManager::VersionManager() : count(0), nextId(1)
{
    ifstream in("codegenome_versions.dat", ios::binary);
    VersionRecord r;
    while(count < 1000 && in.read(reinterpret_cast<char*>(&r), sizeof(r)))
    {
        r.repository[49] = r.file[49] = r.timestamp[39] = '\0';
        r.author[29] = r.message[99] = r.content[499] = '\0';
        if(r.id <= 0) break;
        versions[count++] = r;
        if(r.id >= nextId) nextId = r.id + 1;
    }
}
bool VersionManager::commit(const char repo[], const char file[], const char author[], const char message[], const char content[])
{
    if(count >= 1000) return false;
    VersionRecord r = {};
    r.id = nextId;
    strncpy(r.repository, repo, 49); strncpy(r.file, file, 49);
    strncpy(r.author, author, 29); strncpy(r.message, message, 99);
    strncpy(r.content, content, 499);
    time_t now = time(0);
    tm* local = localtime(&now);
    if(local) strftime(r.timestamp, sizeof(r.timestamp), "%Y-%m-%d %H:%M:%S", local);
    ofstream out("codegenome_versions.dat", ios::binary | ios::app);
    if(!out || !out.write(reinterpret_cast<const char*>(&r), sizeof(r))) return false;
    versions[count++] = r;
    nextId++;
    return true;
}
const VersionRecord* VersionManager::get(int id) const
{
    for(int i = 0; i < count; i++) if(versions[i].id == id) return &versions[i];
    return 0;
}
const VersionRecord* VersionManager::at(int index) const { return index >= 0 && index < count ? &versions[index] : 0; }
int VersionManager::total() const { return count; }
int VersionManager::countFor(const char repo[]) const
{
    int result = 0;
    for(int i = 0; i < count; i++) if(strcmp(versions[i].repository, repo) == 0) result++;
    return result;
}
void VersionManager::history(const char repo[], const char file[]) const
{
    bool found = false;
    for(int i = count - 1; i >= 0; i--)
    {
        const VersionRecord& r = versions[i];
        if(strcmp(r.repository, repo) != 0 || (file[0] && strcmp(r.file, file) != 0)) continue;
        cout << "\n#" << r.id << " | " << r.file << " | " << r.author << " | " << r.timestamp << "\n  " << r.message << endl;
        found = true;
    }
    if(!found) cout << "\nNo matching versions.\n";
}
bool VersionManager::compare(int first, int second) const
{
    const VersionRecord* a = get(first);
    const VersionRecord* b = get(second);
    if(!a || !b || strcmp(a->repository, b->repository) || strcmp(a->file, b->file)) return false;
    cout << "\n--- Version " << first << "\n+++ Version " << second << endl;
    if(strcmp(a->content, b->content) == 0) { cout << "No changes.\n"; return true; }
    cout << "- " << a->content << "\n+ " << b->content << endl;
    return true;
}
bool VersionManager::restore(Repository& repo, int id)
{
    const VersionRecord* r = get(id);
    if(!r || strcmp(repo.getRepoName(), r->repository) != 0) return false;
    return repo.restoreFile(r->file, r->content);
}

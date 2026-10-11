#ifndef VERSION_MANAGER_H
#define VERSION_MANAGER_H
#include "Repository.h"
struct VersionRecord
{
    int id;
    char repository[50], file[50], author[30], message[100], timestamp[40], content[500];
};
class VersionManager
{
    VersionRecord versions[1000];
    int count, nextId;
public:
    VersionManager();
    bool commit(const char repo[], const char file[], const char author[], const char message[], const char content[]);
    void history(const char repo[], const char file[] = "") const;
    bool compare(int first, int second) const;
    bool restore(Repository& repo, int id);
    int total() const;
    int countFor(const char repo[]) const;
    const VersionRecord* get(int id) const;
    const VersionRecord* at(int index) const;
};
#endif

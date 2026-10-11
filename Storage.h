#ifndef STORAGE_H
#define STORAGE_H
#include "Repository.h"
class Storage
{
public:
    static int loadRepositories(Repository repositories[], int capacity);
    static bool saveRepositories(Repository repositories[], int count);
};
#endif

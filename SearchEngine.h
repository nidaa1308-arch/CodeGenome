#ifndef SEARCH_ENGINE_H
#define SEARCH_ENGINE_H
#include "VersionManager.h"
class SearchEngine
{
public:
    static void search(Repository repos[], int count, const VersionManager& versions, const char term[]);
};
#endif

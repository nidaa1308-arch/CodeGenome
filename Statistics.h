#ifndef STATISTICS_H
#define STATISTICS_H
#include "VersionManager.h"
class Statistics
{
public:
    static void show(Repository repos[], int count, const VersionManager& versions);
};
#endif

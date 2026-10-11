#ifndef HISTORY_MANAGER_H
#define HISTORY_MANAGER_H
#include "VersionManager.h"
class HistoryManager
{
public:
    static void timeline(const VersionManager& versions);
};
#endif

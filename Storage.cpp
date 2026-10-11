#include <fstream>
#include <cstring>
#include "Storage.h"
using namespace std;
int Storage::loadRepositories(Repository repositories[], int capacity)
{
    ifstream input("repositories.txt");
    if(!input)
        return 0;
    char line[256], name[50] = "", owner[30] = "";
    int count = 0;
    while(input.getline(line, sizeof(line)))
    {
        if(strncmp(line, "Repository: ", 12) == 0)
        {
            strncpy(name, line + 12, sizeof(name) - 1);
            name[sizeof(name) - 1] = '\0';
        }
        else if(strncmp(line, "Owner: ", 7) == 0)
        {
            strncpy(owner, line + 7, sizeof(owner) - 1);
            owner[sizeof(owner) - 1] = '\0';
        }
        else if(strncmp(line, "--------------------------", 26) == 0)
        {
            if(name[0] && owner[0] && count < capacity)
            {
                bool duplicate = false;
                for(int i = 0; i < count; i++)
                    if(strcmp(repositories[i].getRepoName(), name) == 0)
                        duplicate = true;
                if(!duplicate)
                    repositories[count++] = Repository(name, owner);
            }
            name[0] = '\0';
            owner[0] = '\0';
        }
    }
    return count;
}

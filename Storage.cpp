#include <fstream>
#include <cstring>
#include "Storage.h"
using namespace std;
namespace
{
    struct FileData { char name[50]; char content[500]; };
    struct RepoData { char name[50]; char owner[30]; int count; FileData files[20]; };
}
bool Storage::saveRepositories(Repository repositories[], int count)
{
    ofstream out("codegenome_repos.dat", ios::binary | ios::trunc);
    if(!out) return false;
    out.write(reinterpret_cast<const char*>(&count), sizeof(count));
    for(int i = 0; i < count; i++)
    {
        RepoData r = {};
        strncpy(r.name, repositories[i].getRepoName(), 49);
        strncpy(r.owner, repositories[i].getOwner(), 29);
        r.count = repositories[i].getFileCount();
        for(int j = 0; j < r.count; j++)
        {
            SourceFile* f = repositories[i].getFile(j);
            strncpy(r.files[j].name, f->getFileName(), 49);
            strncpy(r.files[j].content, f->getContent(), 499);
        }
        out.write(reinterpret_cast<const char*>(&r), sizeof(r));
    }
    out.flush();
    return out.good();
}
int Storage::loadRepositories(Repository repositories[], int capacity)
{
    ifstream in("codegenome_repos.dat", ios::binary);
    if(in)
    {
        int count = 0;
        if(!in.read(reinterpret_cast<char*>(&count), sizeof(count)) || count < 0 || count > capacity) return 0;
        for(int i = 0; i < count; i++)
        {
            RepoData r = {};
            if(!in.read(reinterpret_cast<char*>(&r), sizeof(r))) return i;
            r.name[49] = '\0'; r.owner[29] = '\0';
            if(r.count < 0 || r.count > 20) return i;
            repositories[i] = Repository(r.name, r.owner);
            for(int j = 0; j < r.count; j++)
            {
                r.files[j].name[49] = '\0';
                r.files[j].content[499] = '\0';
                repositories[i].restoreFile(r.files[j].name, r.files[j].content);
            }
        }
        return count;
    }
    // Import repositories from the original 40% implementation once.
    ifstream legacy("repositories.txt");
    if(!legacy) return 0;
    char line[256], name[50] = "", owner[30] = "";
    int count = 0;
    while(legacy.getline(line, sizeof(line)))
    {
        if(strncmp(line, "Repository: ", 12) == 0)
        { strncpy(name, line + 12, 49); name[49] = '\0'; }
        else if(strncmp(line, "Owner: ", 7) == 0)
        { strncpy(owner, line + 7, 29); owner[29] = '\0'; }
        else if(strncmp(line, "--------------------------", 26) == 0)
        {
            if(name[0] && owner[0] && count < capacity)
            {
                bool duplicate = false;
                for(int i = 0; i < count; i++)
                    if(strcmp(repositories[i].getRepoName(), name) == 0) duplicate = true;
                if(!duplicate) repositories[count++] = Repository(name, owner);
            }
            name[0] = '\0'; owner[0] = '\0';
        }
    }
    saveRepositories(repositories, count);
    return count;
}

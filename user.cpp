#include <iostream>
#include <cstring>
#include "User.h"
using namespace std;
User::User(char u[], char p[])
{
    strcpy(username, u);
    strcpy(password, p);
}
void User::showRole()
{
    cout << "User";
}
bool User::login(char u[], char p[])
{
    if(strcmp(username, u) == 0 && strcmp(password, p) == 0)
        return true;
    return false;
}
char* User::getUsername()
{
    return username;
}
bool User::canCreateRepository()
{
    return false;
}
User::~User()
{
}
Admin::Admin(char u[], char p[]) : User(u, p)
{
}
void Admin::showRole()
{
    cout << "Admin";
}
bool Admin::canCreateRepository()
{
    return true;
}
Student::Student(char u[], char p[]) : User(u, p)
{
}
void Student::showRole()
{
    cout << "Student";
}
bool Student::canCreateRepository()
{
    return true;
}
Collaborator::Collaborator(char u[], char p[]) : User(u, p)
{
}
void Collaborator::showRole()
{
    cout << "Collaborator";
}
bool Collaborator::canCreateRepository()
{
    return false;
}
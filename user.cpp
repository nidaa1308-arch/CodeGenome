#include <iostream>
#include <cstring>
#include "User.h"
using namespace std;
User::User(const char u[], const char p[])
{
    strncpy(username, u, sizeof(username) - 1);
    username[sizeof(username) - 1] = '\0';
    strncpy(password, p, sizeof(password) - 1);
    password[sizeof(password) - 1] = '\0';
}
void User::showRole() { cout << "User"; }
bool User::login(const char u[], const char p[])
{
    return strcmp(username, u) == 0 && strcmp(password, p) == 0;
}
char* User::getUsername() { return username; }
bool User::canCreateRepository() { return false; }
User::~User() {}
Admin::Admin(const char u[], const char p[]) : User(u, p) {}
void Admin::showRole() { cout << "Admin"; }
bool Admin::canCreateRepository() { return true; }
Student::Student(const char u[], const char p[]) : User(u, p) {}
void Student::showRole() { cout << "Student"; }
bool Student::canCreateRepository() { return true; }
Collaborator::Collaborator(const char u[], const char p[]) : User(u, p) {}
void Collaborator::showRole() { cout << "Collaborator"; }
bool Collaborator::canCreateRepository() { return false; }

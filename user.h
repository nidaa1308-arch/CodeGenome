#ifndef USER_H
#define USER_H
class User
{
protected:
    char username[30];
    char password[30];
public:
    User(char u[] = "", char p[] = "");
    virtual void showRole();
    bool login(char u[], char p[]);
    char* getUsername();
    virtual bool canCreateRepository();
    virtual ~User();
};
class Admin : public User
{
public:
    Admin(char u[], char p[]);
    void showRole();
    bool canCreateRepository();
};
class Student : public User
{
public:
    Student(char u[], char p[]);
    void showRole();
    bool canCreateRepository();
};
class Collaborator : public User
{
public:
    Collaborator(char u[], char p[]);
    void showRole();
    bool canCreateRepository();
};
#endif
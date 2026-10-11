#ifndef USER_H
#define USER_H
class User
{
protected:
    char username[30];
    char password[30];
public:
    User(const char u[] = "", const char p[] = "");
    virtual void showRole();
    bool login(const char u[], const char p[]);
    char* getUsername();
    virtual bool canCreateRepository();
    virtual ~User();
};
class Admin : public User
{
public:
    Admin(const char u[], const char p[]);
    void showRole();
    bool canCreateRepository();
};
class Student : public User
{
public:
    Student(const char u[], const char p[]);
    void showRole();
    bool canCreateRepository();
};
class Collaborator : public User
{
public:
    Collaborator(const char u[], const char p[]);
    void showRole();
    bool canCreateRepository();
};
#endif

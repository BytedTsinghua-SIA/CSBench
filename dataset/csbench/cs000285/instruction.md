# Lab 5: Secure File System

## Introduction

Over the course of the semester, the labs have exposed you to both high-level and low-level security concepts, and you have played the roles of both attacker and defender. In this lab, the goal is to expose you to the challenges of building a secure, relatively complex, and useful piece of software. You will build a remote file system, SecFS, that provides both confidentiality and integrity in the face of a completely untrusted server.

To save you from writing uninteresting boilerplate code, we provide you with a skeleton implementation with few features and fewer security guarantees. It is your job to extend this such that the goals outlined below are all met. The code we provide you with is a partial implementation of the serialized version of SUNDR. You should read the SUNDR paper, as many of the concepts in this lab are taken from there. To complete this lab, you will have to flesh out the rest of the implementation to support the entirety of serialized SUNDR, as well as add confidentiality guarantees (read-protection of files). For the latter, you will need to come up with a reasonable mechanism for encrypting files and distributing keys.

## Motivation

The world is slowly becoming more connected, and there's an increasing need to have all your data be available, shareable, secure, and replicated. Because of this need, cloud services such as Dropbox and Google Drive have emerged, and become wildly successful. They take your files and transparently host them in "the cloud". Unfortunately, users lose some measure of control over that data in the process. You have to trust your data to these companies; you have to trust them not to look at your data, not to share it, and not to lose it. For this lab, your goal is to develop a file system that allows users to store data on a remote file server, without trusting that server, obviating many of these problems.

## Core Tasks

### Exercise 1: Integrity

Your first task is to implement the integrity guarantees of serialized SUNDR. In particular, you must ensure that:

1. **Users can detect unauthorized modifications**: If a user modifies a file or directory, all other users should be able to detect this modification when they next access the file system. This should be true even if the server is malicious and tries to hide the modification.

2. **Users can detect unauthorized deletions**: If a user deletes a file or directory entry, all other users should be able to detect this deletion.

3. **Users cannot impersonate other users**: A user should not be able to make modifications that appear to come from another user.

4. **Fork consistency**: If the server presents different views of the file system to different users, all users should eventually be able to detect this inconsistency.

The skeleton code provides a partial implementation of SUNDR's integrity mechanisms. You will need to complete this implementation to ensure that all of the above properties hold.

### Exercise 2: Group-permissions

SUNDR's integrity guarantees are built around the concept of an i-table (integrity table) that tracks the version numbers of all inodes that a user has modified. However, the skeleton code only supports a single user. Your second task is to extend the implementation to support multiple users and group-based sharing.

In particular, you must implement the following:

1. **Multiple users**: The file system should support multiple users, each with their own public/private key pair.

2. **Group-based sharing**: Users should be able to create files and directories that are writable by a specific group. When a file is group-writable, any user in that group should be able to modify it.

3. **Group membership**: Users should be able to belong to multiple groups. Group membership is defined in the `.groups` file in the root directory.

4. **Permission inheritance**: When a file or directory is created with group permissions, those permissions should be properly enforced and inherited by child entries where appropriate.

The mechanism for specifying group-writeable files (and directories) is by abusing the user's umask(2). The umask of a process determines what permissions will _not_ be granted to newly created files. For example, by setting your umask to `0200`, you are saying that new files should have all bits set _except_ the owner's write bit. SecFS interprets this as making the file group-writeable. Note that using `0200` will cause the file to be shared with the group the user is currently running as; for root, this is usually group 0, so you will want to use the `sg` command to instead operate as the "users" group (group 100).

### Exercise 3: Read-permissions

For this lab, we also require that you implement read-permissions. In particular, if a user specifies that a file is read-protected, its contents should be hidden from the server, as well as from any other user not named in the ACL (i.e. that is not the user who created it, or that is not in the group the creator shared the file with). Note that it is _not_ sufficient to simply check the permission bits on the file; a malicious client or server should not be _able_ to see the file or directory contents, even if they bypass all the permission checks.

Similarly to how we implement group-permissions, we also hijack umask to allow users to express that they do not wish a file to be world-readable. By setting the umask to `0004`, you are _not_ granting world-readable, which SecFS interprets as requesting encryption of the file. This mask can be combined with the group-writeable mask as `0204`, which would indicate a group-writeable file that is only readable by the group.

Your goal for this exercise is to ensure that the contents of files (and directories) that are created with read restrictions are never stored in plaintext on the server, and that their decryption key is not accessible to users who are not permitted to read the file in question. Keep in mind that public-key cryptography operations are slow, so you may want to encrypt the file contents using a symmetric key, and then encrypt the symmetric key such that only allowed users may read it, and hence the file.

We specifically do not require that a user be able to modify who is able to read a file after the fact. This includes if a group changes, and the ACL of the file has technically changed. Furthermore, we do not require that you hide the inode metadata of encrypted files, though you may do so if you wish.

## Implementation Notes

### SUNDR Structure Mapping

To give you a handle on where the different parts of SUNDR that we have already implemented are located, we give here a mapping from Figures 2 and 3 from the SUNDR paper to files in SecFS:

| structure         | location                                                                                 |
| ----------------- | ---------------------------------------------------------------------------------------- |
| i-tables          | secfs/tables.py                                                                          |
| inodes            | secfs/store/inode.py                                                                     |
| directory block   | secfs/store/tree.py                                                                      |
| version structure | has not been implemented, but should probably replace current_itables in secfs/tables.py |

### Development Approach

A good approach to implementing complex systems such as this is to build it in iterations, where each iteration implements a "deeper" part of the system. For example, during early development, you might want to add `decrypt(key, in)` and `encrypt(key, in)` functions, but leave their implementations as `return in`. This simplifies debugging, and lets you focus on fewer problems at any one time.

This lab will take a significant amount of effort, and this is not merely because of volume. You will have to make careful design decisions, and decide why every aspect of your design maintains the required security properties. Start early!

## File System Structure

The file system uses the following key components:

- **i-tables**: Integrity tables that track version numbers of inodes modified by each user
- **inodes**: File and directory metadata structures
- **directory blocks**: Contain directory entries mapping names to inode handles
- **version structures**: Track the version history of the file system

## Security Requirements

The implementation must ensure:

1. **Integrity**: Users can detect unauthorized modifications, deletions, and impersonation attempts
2. **Confidentiality**: File contents are encrypted and only accessible to authorized users
3. **Group-based access control**: Support for multiple users and group-based sharing
4. **Fork consistency**: Detection of inconsistent views presented by a malicious server

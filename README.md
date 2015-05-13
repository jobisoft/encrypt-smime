# encrypt-smime
Automatically encrypt all incoming e-mails using an S/MIME certificate.

## Why?
Only a small percentage of incoming e-mails are encrypted, so almost all
e-mails are stored as plain text on the mailserver. To fix this problem one 
could encrypt all incoming e-mails before storing them. This does not require
any changes to the MUA, it will look like the sender had encrypted the mail.

This script is intended for S/MIME users. A solution for PGP users can be 
found [here](https://github.com/mikecardwell/gpgit).
   
## How?
The *encrypt-smime.py* script takes one argument on the command line: The
public part of an S/MIME certificate. An e-mail message is piped through this
python script and the resulting e-mail is sent to STDOUT encrypted with the
public part of the S/MIME certificate. 

If the message is already encrypted, it doesn't get encrypted a second time.

Exim users can use the transport_filter directive in a transport in order to
call this script, like so:

	transport_filter = /path/to/encrypt-smime.py /path/to/pub.pem

Procmail users can add a procmail recipe as follows

	:0 f
	| /path/to/encrypt-smime.py /path/to/pub.pem
  
## What about the "Sent" folder (IMAP)?
When writing an e-mail, the MUA usually drops a copy of the sent mail into
the "sent" folder, where it is stored unencrypted. There are multiple ways
to fix this. One solution would be to monitor the sent folder with [incrond](http://linux.die.net/man/8/incrond).

Add a incrontab like so:

	/path/to/send/folder/cur IN_CREATE,IN_NO_LOOP /path/to/encrypt_watched_folder.sh $@ $#
	
The bash script *encrypt_watched_folder.sh* is a wrapper for encrypt-smime.py.
It requires at least two arguments (the watched folder name and the name of the 
new message), which are provided by incron via *$@* and *$#*. The optional third 
parameter is the location of the public certificate which should be used to encrypt 
the message. If that is not provided, encrypt_watched_folder.sh assumes the 
certificate is located two levels above the watched folder (which would be the IMAP
root directory).

The bash script needs to know the location of encrypt-smime.py.

# encrypt-smime
Automatically encrypting all incoming e-mails using an S/MIME certificate.

## Why?
Only a small percentage of incoming emails are encrypted, so almost all
emails are stored as plain text on the mailserver. To fix this problem one 
could encrypt all incoming emails before storing them. This does not require
any changes to the MUA, it looks like the sender had encrypted the mail.

This script is intended for S/MIME users. A solution for PGP users can be 
found [here](https://github.com/mikecardwell/gpgit).
   
## How?
The encrypt-smime.py script takes one argument on the command line: The
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
When writing an email, the MUA usually drops a copy of the sent mail into
the "sent" folder, where it is stored unencrypted. There are multiple ways
to fix this. One solution would be to monitor the sent folder with [incrond](http://linux.die.net/man/8/incrond).

Add a incrontab like so:

	/path/to/send/folder/cur IN_CREATE,IN_NO_LOOP /path/to/encrypt_watched_folder.sh $@ $#
	
The bash script is a wrapper for encrypt-smime.py.




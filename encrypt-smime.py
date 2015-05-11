#!/usr/bin/python

##############################################################################
#                                                                            #
# Copyright 2015, Jakob Bieling & John Bieling                               #
#                                                                            #
# https://github.com/jobisoft/encrypt-smime                                  #
#                                                                            #
# This program is free software; you can redistribute it and/or modify       #
# it under the terms of the GNU General Public License as published by       #
# the Free Software Foundation; either version 2 of the License, or          #
# any later version.                                                         #
#                                                                            #
# This program is distributed in the hope that it will be useful,            #
# but WITHOUT ANY WARRANTY; without even the implied warranty of             #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
# GNU General Public License for more details.                               #
#                                                                            #
# You should have received a copy of the GNU General Public License          #
# along with this program; if not, write to the Free Software                #
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA #
#                                                                            #
##############################################################################

import sys, string, uuid, re, os.path, socket
from M2Crypto import BIO, Rand, SMIME, X509


def parseHeader(hdr):
  headerLines = hdr.split (lineFeedType)
  header = []

  for line in headerLines:
    if line [0] != ' ' and line [0] != '\t':
      header.append (line)
    else:
      header [-1] += lineFeedType + line

  return header


def isContentTypeEncrypted(hdr):
  isEncrypted = re.search ("""^Content-Type:.*smime-type[ ]*=[ "']*enveloped-data""", hdr, re.DOTALL) != None
  return isEncrypted










# Read full message from stdin.
emailData = sys.stdin.read ()
lineFeedType = ""



# A missing pubKey is not an error, the user decided not to provide one.
pubKeyIsGiven = len (sys.argv) > 1 and os.path.isfile (sys.argv[1])
if not pubKeyIsGiven:
  sys.stdout.write (emailData)
  sys.exit (0)



# Split headers from body.
lineFeedType = "\r\n"
emailParts = emailData.split (lineFeedType + lineFeedType, 1)
if len(emailParts) == 1:
  lineFeedType = "\n"
  emailParts = emailData.split (lineFeedType + lineFeedType, 1)

unableToSplitHeaderFromBody = (len(emailParts) == 1)
if unableToSplitHeaderFromBody:
  sys.stdout.write (emailData)
  sys.exit (0)

emailHeader = emailParts [0]
emailBody = emailParts [1]



# Split header into individual header elements.
parsedHeader = parseHeader(emailHeader)

isAlreadyEncrypted = any(isContentTypeEncrypted(hdr) for hdr in parsedHeader)
if isAlreadyEncrypted:
  sys.stdout.write (emailData)
  sys.exit (0)

# Filter and sort header elements.
emailContentHeaders = lineFeedType.join (filter(lambda x: x.lower().startswith("content-"), parsedHeader))
emailNonContentHeaders = lineFeedType.join (filter(lambda x: not x.lower().startswith("content-") and not x.lower().startswith("mime-version:") and not x.lower().startswith("message-id:"), parsedHeader))
emailOriginalMessageID = lineFeedType.join (filter(lambda x: x.lower().startswith("message-id:"), parsedHeader))


# Generate new body, which will be encrypted.
emailUUID = str (uuid.uuid1 ())
emailBoundaryString = '==_Part_' + emailUUID
emailNewBody = 'Content-Type: multipart/mixed; boundary="' + emailBoundaryString + '"' + lineFeedType
emailNewBody += lineFeedType
emailNewBody += '--' + emailBoundaryString + lineFeedType
emailNewBody += emailContentHeaders + lineFeedType
emailNewBody += lineFeedType
emailNewBody += emailBody + lineFeedType
emailNewBody += '--' + emailBoundaryString + '--' + lineFeedType



# Seed the random number generator with 1024 random bytes (8192 bits).
Rand.rand_seed (os.urandom (1024))

# An invalid key is an error, tell user via X-Crypt-Header.
try:
  pubKeyIsInvalid = False
  cert = X509.load_cert (sys.argv[1])
  x509Stack = X509.X509_Stack ()
  x509Stack.push (cert)
except:
  pubKeyIsInvalid = True

if pubKeyIsInvalid:
  sys.stdout.write ("X-Crypt: Encryption by <" + socket.gethostname()+ "> failed due to bad key." + lineFeedType)
  sys.stdout.write (emailData)
  sys.exit (0)


# Encrypt message.
smimeObj = SMIME.SMIME ()
smimeObj.set_x509_stack (x509Stack)
smimeObj.set_cipher (SMIME.Cipher ('des_ede3_cbc'))
encryptedEmailBody = smimeObj.encrypt (BIO.MemoryBuffer (emailNewBody))


# Compose encrypted email out of prepared parts.
# According to RFC 822 and RFC 2822, every email must have a message
# field ID that "provides a unique message identifier that refers to a
# particular version of a particular message. The uniqueness of 
# the message identifier is guaranteed by the host that generates it"
# Therefore, a new message ID must be genereated.
out = BIO.MemoryBuffer ()
out.write ("X-Crypt: This message has been encrypted by <" + socket.gethostname() + ">" + lineFeedType)
out.write ("Message-ID: " + emailUUID + "@" + socket.gethostname() + lineFeedType)
out.write ("X-Original-" + emailOriginalMessageID + lineFeedType)
out.write (emailNonContentHeaders + lineFeedType)
smimeObj.write (out, encryptedEmailBody)
print out.read ()


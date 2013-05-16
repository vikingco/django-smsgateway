# SMPP_PORT specified the port that SMPPSim will listen on for connections from SMPP
# clients. SMPP_CONNECTION_HANDLERS determines the maximum number of client connections
# that can be handled concurrently.
SMPP_PORT=2777
SMPP_CONNECTION_HANDLERS=10

# Specify the classes that imlement connection and protocol handling respectively here.
# Such classes *must* be subclasses of com.seleniumsoftware.SMPPSim.ConnectionHandler and com.seleniumsoftware.SMPPSim.SMPPProtocolHandler respectively
# Or those classes themselves for the default (good) behaviour
# Supply your own subclasses with particular methods overridden if you want to implement
# bad SMSC behaviours to see how your client application copes...
CONNECTION_HANDLER_CLASS=com.seleniumsoftware.SMPPSim.StandardConnectionHandler
PROTOCOL_HANDLER_CLASS=com.seleniumsoftware.SMPPSim.StandardProtocolHandler

# Specify the class that implements the message state life cycle simulation.
# Such classes must extend the default class, LifeCycleManager
LIFE_CYCLE_MANAGER=com.seleniumsoftware.SMPPSim.LifeCycleManager
#
# The Deterministic Lifecycle Manager sets message state according to the first character of the message destination address:
# 1=EXPIRED,2=DELETED,3=UNDELIVERABLE,4=ACCEPTED,5=REJECTED, other=DELIVERED
# LIFE_CYCLE_MANAGER=com.seleniumsoftware.SMPPSim.DeterministicLifeCycleManager

# LifeCycleManager parameters
#
# Check and possibly change the state of messages in the OutboundQueue every n milliseconds
MESSAGE_STATE_CHECK_FREQUENCY=5000

# Maximum time (in milliseconds) in the initial ENROUTE state
MAX_TIME_ENROUTE=10000

# Percentage of messages that change state each time we check (excluding expiry or messages being completely discarded due to age)
# Requires an integer between 0 and 100
PERCENTAGE_THAT_TRANSITION=75

# State transition percentages. These parameters define the percentage of messages that
# transition from ENROUTE to the specified final state. The list of percentages should
# add up to 100 and must be integer values. SMPPSim will adjust the percentages if they do not.

# Percentage of messages that will transition from ENROUTE to DELIVERED
PERCENTAGE_DELIVERED=90

# Percentage of messages that will transition from ENROUTE to UNDELIVERABLE
PERCENTAGE_UNDELIVERABLE=6

# Percentage of messages that will transition from ENROUTE to ACCEPTED
PERCENTAGE_ACCEPTED=2

# Percentage of messages that will transition from ENROUTE to REJECTED
PERCENTAGE_REJECTED=2

# Time messages held in queue before being discarded, after a final state has been reached (milliseconds)
# For example, after transitioning to DELIVERED (a final state), state info about this message will be
# retained in the queue for a further (e.g.) 60000 milliseconds before being deleted.
DISCARD_FROM_QUEUE_AFTER=60000

# Web Management
HTTP_PORT=90
HTTP_THREADS=1
DOCROOT=www
AUTHORISED_FILES=/css/style.css,/index.htm,/inject_mo.htm,/favicon.ico,/images/logo.gif,/images/dots.gif,/user-guide.htm,/images/homepage.gif,/images/inject_mo.gif
INJECT_MO_PAGE=/inject_mo.htm

# Account details. One account only can be specified. SystemID and Password provided in Binds will be validated against these credentials.
SYSTEM_IDS=smppclient
PASSWORDS=password

# MO SERVICE
DELIVERY_MESSAGES_PER_MINUTE=1
DELIVER_MESSAGES_FILE=deliver_messages.csv

# LOOPBACK
LOOPBACK=FALSE

# QUEUES
# Maximum size parameters are expressed as max number of objects the queue can hold
OUTBOUND_QUEUE_MAX_SIZE=1000
INBOUND_QUEUE_MAX_SIZE=1000

# LOGGING
# See logging.properties for configuration of the logging system as a whole
#
# Set the following property to true to have each PDU logged in human readable
# format. Uses INFO level logging so the log level must be set accordingly for this
# output to appear.
DECODE_PDUS_IN_LOG=true

# PDU CAPTURE
# The following properties allow binary and/or decoded PDUs to be captured in files
# This is to allow the results of test runs (especially regression testing) to be
# checked with reference to these files
#
# Note that currently you must use the StandardConnectionHandler and StandardProtocolHandler classes for this
# feature to be available.
#
# _SME_ properties concern PDUs sent from the SME application to SMPPSim
# _SMPPSIM_ properties concern PDUs sent from SMPPSim to the SME application
#
CAPTURE_SME_BINARY=false
CAPTURE_SME_BINARY_TO_FILE=sme_binary.capture
CAPTURE_SMPPSIM_BINARY=false
CAPTURE_SMPPSIM_BINARY_TO_FILE=smppsim_binary.capture
CAPTURE_SME_DECODED=false
CAPTURE_SME_DECODED_TO_FILE=sme_decoded.capture
CAPTURE_SMPPSIM_DECODED=false
CAPTURE_SMPPSIM_DECODED_TO_FILE=smppsim_decoded.capture

# Byte Stream Callback
#
# This feature, if enabled, will cause SMPPSim to send PDUs received from the ESME or sent to it 
# as byte streams over a couple of connections.
# This is intended to be useful in automated testing scenarios where you need to notify the test application
# with details of what was *actually* received by SMPPSim (or sent by it).
#
# Note that byte streams are prepended by the following fields:
#
# a 4 byte integer which indicates the length of the whole callback message
# a 1 byte indicator of the type of interaction giving rise to the callback, 
# - where 0x01 means SMPPSim received a request PDU and 
#         0x02 means SMPPSim sent a request PDU (e.g. a DeliverSM)
# a 4 byte fixed length identified, which identifies the SMPPSim instance that sent the bytes
#
# So the length of the SMPP pdu is the callback message length - 9.
#
# LENGTH(4) TYPE(1) ID(4) PDU (LENGTH)
CALLBACK=false
CALLBACK_ID=SIM1
CALLBACK_TARGET_HOST=localhost
CALLBACK_PORT=3333

# MISC
SMSCID=SMPPSim

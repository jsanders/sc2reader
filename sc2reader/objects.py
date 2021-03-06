class Attribute(object):
    
    def __init__(self, data):
        #Unpack the data values and add a default name of unknown to be
        #overridden by known attributes; acts as a flag for exclusion
        self.header, self.id, self.player, self.value, self.name = tuple(data+["Unknown"])
        
        #Clean the value of leading null bytes and decode it for easier and more
        #readable comparisons in the decoding logic to follow
        while(self.value[:2] == "00"):
            self.value = self.value[2:]
        self.value = self.value.decode("hex")
        
        
        if self.id == 0x01F4:
            self.name = "Player Type"
            if   self.value == "Humn": self.value = "Human"
            elif self.value == "Comp": self.value = "Computer"
            
        elif self.id == 0x07D1:
            self.name = "Game Type"
            
        elif self.id == 0x0BB8:
            self.name = "Game Speed"
            if   self.value == "Slor": self.value = "Slower"
            elif self.value == "Norm": self.value = "Normal"
            elif self.value == "Fasr": self.value = "Faster"
            
        elif self.id == 0x0BB9:
            self.name = "Race"
            if   self.value.lower() == "prot": self.value = "Protoss"
            elif self.value.lower() == "terr": self.value = "Terran"
            elif self.value.lower() == "rand": self.value = "Random"
            
        elif self.id == 0x0BBA:
            self.name = "Color"
            if   self.value == "tc01": self.value = "Red"
            elif self.value == "tc02": self.value = "Blue"
            elif self.value == "tc03": self.value = "Teal"
            elif self.value == "tc04": self.value = "Purple"
            elif self.value == "tc05": self.value = "Yellow"
            elif self.value == "tc06": self.value = "Orange"
            elif self.value == "tc07": self.value = "Green"
            elif self.value == "tc08": self.value = "Pink"
            
        elif self.id == 0x0BBB:
            self.name = "Handicap"
            
        elif self.id == 0x0BBC:
            self.name = "Difficulty"
            if   self.value == "VyEy": self.value = "Very Easy"
            elif self.value == "Medi": self.value = "Medium"
            elif self.value == "VyHd": self.value = "Very Hard"
            elif self.value == "Insa": self.value = "Insane"
            
        elif self.id == 0x0BC1:
            self.name = "Category"
            if   self.value == "Priv": self.value = "Private"
            elif self.value == "Amm": self.value = "Ladder"
            
        elif self.id == 0x07D2:
            self.name = "Teams1v1"
            #Get the raw team number
            self.value = int(self.value[1:])
            
        elif self.id == 0x07D3:
            self.name = "Teams2v2"
            #Get the raw team number
            self.value = int(self.value[1:], 16)
            
        elif self.id == 0x07D4:
            self.name = "Teams3v3"
            #Get the raw team number
            self.value = int(self.value[1:])
            
        elif self.id == 0x07D5:
            self.name = "Teams4v4"
            #Get the raw team number
            self.value = int(self.value[1:])
            
        elif self.id == 0x07D6:
            self.name = "TeamsFFA"
            #Get the raw team number
            self.value = int(self.value[1:])
            
        #print "%s (%s) - %s - %s" % (self.name, self.id, self.player, self.value)
    
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        return "%s: %s" % (self.name, self.value)


		
		
class Event(object):
    def __init__(self, elapsed_time, event_type, event_code, global_flag, player_id, 
                    location=None, bytes=""):
        self.time, seconds = (elapsed_time, elapsed_time/16)
        self.timestr = "%s:%s" % (seconds/60, str(seconds%60).rjust(2, "0"))
        self.type = event_type
        self.code = event_code
        self.local = (global_flag == 0x0)
        self.player = player_id
        self.location = location
        self.bytes = bytes
		
    def __call__(self, elapsed_time, event_type, global_flag, player_id, event_code, bytes):
        self.time, seconds = (elapsed_time, elapsed_time/16)
        self.timestr = "%s:%s" % (seconds/60, str(seconds%60).rjust(2, "0"))
        self.type = event_type
        self.code = event_code
        self.local = (global_flag == 0x0)
        self.player = player_id
        self.bytes = ""
        self.parse(bytes)
        return self
	
    def __str__(self):
        return "%s - %s" % (self.timestr, self.name)
        
    def __repr__(self):
        return str(self)

class Message(object):
    
    def __init__(self, time, player, target, text):
        self.time, self.player, self.target, self.text = time, player, target, text
        self.sent_to_all = (self.target == 0)
        self.sent_to_allies = (self.target == 2)
        
    def __str__(self):
        time = ((self.time/16)/60, (self.time/16)%60)
        return "%s - Player %s - %s" % (time, self.player.pid, self.text)
        
    def __repr__(self):
        return str(self)


		
class Player(object):
    
    url_template = "http://%s.battle.net/sc2/en/profile/%s/%s/%s/"
    
    def __init__(self, pid, data, realm="us"):
        # TODO: get a map of realm,subregion => region in here
        self.pid = pid
        self.realm = realm
        self.name = data[0].decode("hex")
        self.uid = data[1][4]
        self.subregion = data[1][2]
        self.url = self.url_template % (self.realm, self.uid, self.subregion, self.name)
        self.actual_race = data[2].decode("hex")
        self.choosen_race = "" # Populated from the replay.attribute.events file
        self.rgba = dict([
                ['r', data[3][1]], 
                ['g', data[3][2]], 
                ['b', data[3][3]], 
                ['a', data[3][0]], 
            ])
        self.recorder = True # Actual recorder will be determined using the replay.message.events file
        self.handicap = data[6]
        self.team = None # A number to be supplied later
        self.type = "" # Human or Computer
        
    def __str__(self):
        return "Player %s - %s (%s)" % (self.pid, self.name, self.actual_race)
        
    def __repr__(self):
        return str(self)

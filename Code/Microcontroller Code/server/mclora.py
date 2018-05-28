#LoRa Serial Handle - Send Commands and Handle the response
#Import the Modules Required
import serial

'''****************************************************************************************
Class Name          :   MCLoRa
Description         :   Handle LoRa Events
****************************************************************************************'''
class MCLoRa:
    def __init__(self, port):
        """Conctructor - needs serial port string."""
        self.ser = serial.Serial(port, 57600)

    '''****************************************************************************************
    Function Name       :   testOK
    Description         :   Check module is working
    Parameters          :   none
    ****************************************************************************************'''
    def testOK(self):
        """Tests communication with Microchip Lora Module."""
        # send:
        # sys get ver
        # expect:
        # RN2483 0.9.5 Mar 24 2015 14:15:33
        try:
            self.ser.write("sys reset\r\n".encode())
            s = self.ser.readline().decode().split()
            if s[0] == 'RN2483':
                return (s[0], s[1], " ".join(s[2:]))
            else:
                return False
        except Exception as error:
            print error
            self.ser.write("sys get ver\r\n".encode())
            s = self.ser.readline().decode().split()
            if s[0] == 'RN2483':
                return (s[0], s[1], " ".join(s[2:]))
            else:
                return False

    '''****************************************************************************************
    Function Name       :   pause
    Description         :   Pause MAC Operation and continue with radio
    Parameters          :   none
    ****************************************************************************************'''       
    def pause(self):
        """Pauses LoRaWAN stack."""
        self.ser.write('mac resume\r\n'.encode())
        val = self.ser.readline().decode()
        self.ser.write('mac pause\r\n'.encode())
        val = self.ser.readline().decode()
        return val
    '''****************************************************************************************
    Function Name       :   recv
    Description         :   Receive Data over LoRa
    Parameters          :   none
    ****************************************************************************************'''
    def recv(self):
        """Waits for data. This call will block. 
        """
        # start receive - will block
        self.ser.write('radio rx 0\r\n'.encode())
        # get response
        val = self.ser.readline().decode().strip()
        data = None
        if val == 'ok':
            data = self.ser.readline().split()
            print(data)
        # expected:
        # radio_rx <data>
        if data[0] == 'radio_rx':
            data = data[1]
        return data

    '''****************************************************************************************
    Function Name       :   getUniqueID
    Description         :   Obtain the Unique ID
    Parameters          :   none
    ****************************************************************************************'''
    def getUniqueID(self):
        """Get globally unique number provided by Microchip.
        """
        # example:
        # sys get hweui
        # 0004A30B001AF09E
        self.ser.write('sys get hweui\r\n'.encode())
        id = self.ser.readline().decode().strip()
        return id

    '''****************************************************************************************
    Function Name       :   send
    Description         :   Send the data over LoRa 
    Parameters          :   none
    ****************************************************************************************'''
    def send(self):
        """Waits for data. This call will block. 
        """
        # start receive - will block
        self.ser.write('radio tx 01\r\n'.encode())
        # get response
        val = self.ser.readline().decode().strip()
        print val
        if val == 'ok':
            data = self.ser.readline().split()
            print(data)
        if data[0] == 'radio_tx_ok':
            data = data[0]
        return data

#End of the Script 
##*****************************************************************************************************##
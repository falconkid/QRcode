import Tkinter as tk

import zbar

from PIL import Image
import cv2

import time
import datetime

# Which code should this program stop
Start_Code=['start']
End_Code=['jizz','stop']

# Set sold out time
_sold_time=10.00

def main():
    """
    A simple function that captures webcam video utilizing OpenCV. The video is then broken down into frames which
    are constantly displayed. The frame is then converted to grayscale for better contrast. Afterwards, the image
    is transformed into a numpy array using PIL. This is needed to create zbar image. This zbar image is then scanned
    utilizing zbar's image scanner and will then print the decodeed message of any QR or bar code. To quit the program,
    press "q".
    :return:
    """

    # Begin capturing video. You can modify what video source to use with VideoCapture's argument. It's currently set
    # to be your webcam.
    capture = cv2.VideoCapture(1)

    f=open('Drink_Data.txt','r')

    _items={
        'drink0001':0,
        'drink0002':0,
        'drink0003':0,
        'drink0004':0,
        'drink0005':0
    }

    _items_name={
    	'drink0001':'Coke',
        'drink0002':'Shit',
        'drink0003':'Jizz',
        'drink0004':'Asss',
        'drink0005':'Beer'
    }

    _items_price={
        'drink0001':1,
        'drink0002':2,
        'drink0003':3,
        'drink0004':4,
        'drink0005':5
    }

    _items_time={
        'drink0001':time.time(),
        'drink0002':time.time(),
        'drink0003':time.time(),
        'drink0004':time.time(),
        'drink0005':time.time()
    }

    _items_sold={
        'drink0001':0,
        'drink0002':0,
        'drink0003':0,
        'drink0004':0,
        'drink0005':0
    }
    Sold_Number=0
    Total_Cost=0

    _sold_data=f.readline()
    print _sold_data
    for i in range(5):
        print _sold_data[i]
        if _sold_data[i]=='1':
            _items_sold['drink000'+chr(1+i+ord('0'))]=1
            Sold_Number+=1
            Total_Cost+=_items_price['drink000'+chr(1+i+ord('0'))]

    f.close()

    # Set new window
    win=tk.Tk()
    win.title('Test GUI')
    win.resizable(0,0) # cannot be resized
    win.geometry("1000x800") # size

    GUI_title=tk.Label(win,
        text="Hotel Fridge Management System",
		font=('Arial',24))
    GUI_title.pack() # show label

    B_title=tk.Label(win,
        text='Beverage        Amount  Price  Bought',
        font=('Arial',14),
        width=100,
        height=1)
    B_title.pack()

    Bev_l=[]
    _i_num=0
    for i in range(5):
        Bev_l.append(tk.Label(win,
            text=_items_name['drink000'+chr(1+i+ord('0'))]+'    '+chr(1-_items_sold['drink000'+chr(1+i+ord('0'))]+ord('0'))+'    '+str(_items_price['drink000'+chr(1+i+ord('0'))])+'    '+chr(_items_sold['drink000'+chr(1+i+ord('0'))]+ord('0')),
            font=('Arial',14),
            width=100,
            height=1))
        Bev_l[i].pack()
        _i_num+=1

    TPrice=tk.Label(win,
        text='Total Cost: '+str(Total_Cost)+' NTD',
        font=('Arial',14),
        width=100,
        height=1)
    TPrice.pack()

    #win.mainloop()
    win.update_idletasks()
    win.update()

    REC=open('Purchase_Rec.txt','a')

    while True:
        # To quit this program press q.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Breaks down the video into frames
        ret, frame = capture.read()

        # Displays the current frame
        cv2.imshow('Current', frame)

        # Converts image to grayscale.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Uses PIL to convert the grayscale image into a ndary array that ZBar can understand.
        image = Image.fromarray(gray)
        width, height = image.size
        zbar_image = zbar.Image(width, height, 'Y800', image.tobytes())

        # Scans the zbar image.
        scanner = zbar.ImageScanner()
        scanner.scan(zbar_image)

        # Prints data from image.
        cnt=0
        decoded_code=[]
        for decoded in zbar_image:
            cnt+=1
            decoded_code.append(decoded.data)
            #print(decoded.data)
        #print(cnt)

        # Set when does the program stops
        End_Point=0
        for _dcode in decoded_code:
            for _ecode in End_Code:
                if _dcode==_ecode:
                    End_Point=1
                    break
            if End_Point==1:
                break
        if End_Point==1:
            break

        # Update dictionary _items
        for i in _items:
            if _items_sold[i]==1:
                continue
            _check=0
            for _dcode in decoded_code:
                if _items[i]>0 and i==_dcode:
                    _items_time[i]=time.time()
                    _check=1
                    continue
                if _items[i]==0 and i==_dcode:
                    _items_time[i]=time.time()
                    _items[i]=1
                    _check=1
            if _items[i]==0 and _check==0:
                if time.time()-_items_time[i]>_sold_time:
                    print 'Item',i,'sold out!'
                    _items_sold[i]=1
                    
                    REC.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' : bought '+i+' , total: '+str(Total_Cost)+' -> '+str(Total_Cost+_items_price[i])+'\n')
                    Bev_l[ord(i[-1])-ord('0')-1].configure(text=_items_name[i]+'    '+chr(1-_items_sold[i]+ord('0'))+'    '+str(_items_price[i])+'    '+chr(_items_sold[i]+ord('0')))
                    
                    Total_Cost+=_items_price[i]
                    TPrice.configure(text='Total Cost: '+str(Total_Cost)+' NTD')
                    
                    Sold_Number+=1
                    f=open('Drink_Data.txt','w')
                    ch=''
                    for j in range(5):
                        ch+=chr(ord('0')+_items_sold['drink000'+chr(1+j+ord('0'))])
                    f.write(ch)
                    f.close()

            if _items[i]>0 and _check==0:
                _items[i]=0

        if Sold_Number==len(_items_sold):
            print 'All items were sold!'
            break

        for i in _items:
            if _items_sold[i]==1:
                continue
            print i, _items[i]

        win.update_idletasks()
        win.update()

    f=open('Cost_Rec.txt','w')
    f.write(str(Total_Cost))
    f.close()
    REC.close()


if __name__ == "__main__":
    main()

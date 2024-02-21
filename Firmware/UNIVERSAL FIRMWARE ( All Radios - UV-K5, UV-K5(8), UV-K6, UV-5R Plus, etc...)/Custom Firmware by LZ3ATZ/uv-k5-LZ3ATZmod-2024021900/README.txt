.!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!                                                       !!!
!!! This firmware is for radios with replaced EEPROM chip !!!
!!!                                                       !!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'

I. EEPROM replacement
  1. Backup the eeprom (k5prog, k5prog-win)
     (How? - You must already know how to do this...)
  2. Replace the eeprom with AT24C128, AT24C256 or AT24C512 (or compatible)
  3. Restore the eeprom (k5prog, k5prog-win)
  4. Test that the device is working as expected with the new eeprom

II. Firmware update
-------------------
  1. Install the firmware from the folder matching the installed eeprom
     (firmware-AT24C128, 256, 512)
     (How? - You must already know how to do this...)

III. Reset the the device
-------------------------
  1. Turn off the radio
     (How? - You must already know how to do this...)
  2. Pres and hold PTT and the key just below PTT, then turn ON the radio
      with the volume knob.
  3. Press the UP key to select "Reset"
  4. Press Menu key to enter the selection
  5. Press UP key to change from 'VFO' to 'ALL'
  6. Press MENU key to select, repeat to confirm the selection

IV. CHIRP Driver Load
----------------------------
  1. Enable Developer Mode in CHIRP
    1.1 Go to Help --> Check "Developer Mode"
    1.2 Restart CHIRP
  2. Load uvk5_LZ3ATZmod.py in CHIRP
    2.1 Go to File --> "Load Module"
    2.2 Read the warning message and Accept if agree with the text
    2.3 Navigate to chirp/uvk5_LZ3ATZmod.py from this archive and Open it
   
V. Using CHIRP
--------------
  1. Select Radio --> "Download from radio..."
  2. Choose Port, Vendor: Quansheng, Model: UV-K5-LZ3ATZmod
  3. Click OK to start downloading the configuration from the radio
  4. Do some edits
  5. Select Radio --> "Upload to radio..."
  6. Click Ok to upload to the radio


[*] The modified firmware will be auto-detected based on the firmware string.

Notes:
 * Use at own risk! Probably there are bugs lurking in the code so, make eeprom backups!
 * The factory reset enables the DTMF Kill option. If there is a DTMF kill event written the radio will be locked.
   Use CHIRP driver to disable DTMF lock feature


Source code of the binaries: https://github.com/ANTodorov/uv-k5-firmware-custom.egzumer/commit/dd60c52573816a126cfa420050029f7c70f502f0


Have Fun!
Anton Todorov / LZ3ATZ
73

Changelog
-------------
v0.1 20240215
 - initial release

v0.2 20230216
 - fixed bug 0x0E78 eeprom map

v0.3 2023021600
 - Restored egzumer driver to work,
 - Added variants for
   24C128 - 239 channels (sorry no much gain, probably will fix with later upodate but no promices given)
   24C256 - 736 channels
   24C512 - 999 channels (the eeprom have space for more but the UI should be changed to handle 4 digit channels)

v0.4 2023021601
 - Prepared a single driver file from the CHIRP drivers.
 - Fixed some more 200 channel limits 

v0.4 2023021700
 - Fix in the Factory reset of the extended region (above 8k)
 - removed separated chirp drivers as they are confusing

v0.5 2023021900
 - Fix MR channel input via the keysi. Thanks Mike Richter DD1MR for reporting the issue!
 - Found one more channel index issue when (re)storing Primary Scanlist channels


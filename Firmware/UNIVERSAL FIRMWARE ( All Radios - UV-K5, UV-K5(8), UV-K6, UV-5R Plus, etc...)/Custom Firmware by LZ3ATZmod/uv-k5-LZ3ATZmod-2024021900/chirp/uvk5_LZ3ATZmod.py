# Quansheng UV-K5 driver (c) 2023 Jacek Lipkowski <sq5bpf@lipkowski.org>
#
# based on template.py Copyright 2012 Dan Smith <dsmith@danplanet.com>
#
#
# This is a preliminary version of a driver for the UV-K5
# It is based on my reverse engineering effort described here:
# https://github.com/sq5bpf/uvk5-reverse-engineering
#
# Warning: this driver is experimental, it may brick your radio,
# eat your lunch and mess up your configuration.
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import struct
import logging

from chirp import chirp_common, directory, bitwise, memmap, errors, util
from chirp.settings import RadioSetting, RadioSettingGroup, \
    RadioSettingValueBoolean, RadioSettingValueList, \
    RadioSettingValueInteger, RadioSettingValueString, \
    RadioSettings, InvalidValueError, RadioSettingSubGroup

LOG = logging.getLogger(__name__)

# Show the obfuscated version of commands. Not needed normally, but
# might be useful for someone who is debugging a similar radio
DEBUG_SHOW_OBFUSCATED_COMMANDS = False

# Show the memory being written/received. Not needed normally, because
# this is the same information as in the packet hexdumps, but
# might be useful for someone debugging some obscure memory issue
DEBUG_SHOW_MEMORY_ACTIONS = False

MEM_FORMAT = """
#seekto 0xe40;
ul16 fmfreq[20];

#seekto 0xe78;
u8 backlight_min:4,
backlight_max:4;

u8 channel_display_mode;
u8 crossband;
u8 battery_save;
u8 dual_watch;
u8 backlight_time;
u8 ste;
u8 freq_mode_allowed;

#seekto 0xe90;
u8 keyM_longpress_action:7,
    button_beep:1;

u8 key1_shortpress_action;
u8 key1_longpress_action;
u8 key2_shortpress_action;
u8 key2_longpress_action;
u8 scan_resume_mode;
u8 auto_keypad_lock;
u8 power_on_dispmode;
ul32 password;

#seekto 0xea0;
u8 voice;
u8 s0_level;
u8 s9_level;

#seekto 0xea8;
u8 alarm_mode;
u8 roger_beep;
u8 rp_ste;
u8 TX_VFO;
u8 Battery_type;

#seekto 0xeb0;
char logo_line1[16];
char logo_line2[16];

//#seekto 0xed0;
struct {
    u8 side_tone;
    char separate_code;
    char group_call_code;
    u8 decode_response;
    u8 auto_reset_time;
    u8 preload_time;
    u8 first_code_persist_time;
    u8 hash_persist_time;
    u8 code_persist_time;
    u8 code_interval_time;
    u8 permit_remote_kill;

    #seekto 0xee0;
    char local_code[3];
    #seek 5;
    char kill_code[5];
    #seek 3;
    char revive_code[5];
    #seek 3;
    char up_code[16];
    char down_code[16];
} dtmf;

#seekto 0xf40;
u8 int_flock;
u8 int_350tx;
u8 int_KILLED;
u8 int_200tx;
u8 int_500tx;
u8 int_350en;
u8 int_scren;


u8  backlight_on_TX_RX:2,
    AM_fix:1,
    mic_bar:1,
    battery_text:2,
    live_DTMF_decoder:1,
    unknown:1;


#seekto 0x1c00;
struct {
char name[8];
char number[3];
#seek 5;
} dtmfcontact[16];

struct {
    struct {
        #seekto 0x1E00;
        u8 openRssiThr[10];
        #seekto 0x1E10;
        u8 closeRssiThr[10];
        #seekto 0x1E20;
        u8 openNoiseThr[10];
        #seekto 0x1E30;
        u8 closeNoiseThr[10];
        #seekto 0x1E40;
        u8 closeGlitchThr[10];
        #seekto 0x1E50;
        u8 openGlitchThr[10];
    } sqlBand4_7;

    struct {
        #seekto 0x1E60;
        u8 openRssiThr[10];
        #seekto 0x1E70;
        u8 closeRssiThr[10];
        #seekto 0x1E80;
        u8 openNoiseThr[10];
        #seekto 0x1E90;
        u8 closeNoiseThr[10];
        #seekto 0x1EA0;
        u8 closeGlitchThr[10];
        #seekto 0x1EB0;
        u8 openGlitchThr[10];
    } sqlBand1_3;

    #seekto 0x1EC0;
    struct {
        ul16 level1;
        ul16 level2;
        ul16 level4;
        ul16 level6;
    } rssiLevelsBands3_7;

    struct {
        ul16 level1;
        ul16 level2;
        ul16 level4;
        ul16 level6;
    } rssiLevelsBands1_2;

    struct {
        struct {
            u8 lower;
            u8 center;
            u8 upper;
        } low;
        struct {
            u8 lower;
            u8 center;
            u8 upper;
        } mid;
        struct {
            u8 lower;
            u8 center;
            u8 upper;
        } hi;
        #seek 7;
    } txp[7];

    #seekto 0x1F40;
    ul16 batLvl[6];

    #seekto 0x1F50;
    ul16 vox1Thr[10];

    #seekto 0x1F68;
    ul16 vox0Thr[10];

    #seekto 0x1F80;
    u8 micLevel[5];

    #seekto 0x1F88;
    il16 xtalFreqLow;

    #seekto 0x1F8E;
    u8 volumeGain;
    u8 dacGain;
} cal;


#seekto 0x1FF0;
struct {
u8 ENABLE_DTMF_CALLING:1,
   ENABLE_PWRON_PASSWORD:1,
   ENABLE_TX1750:1,
   ENABLE_ALARM:1,
   ENABLE_VOX:1,
   ENABLE_VOICE:1,
   ENABLE_NOAA:1,
   ENABLE_FMRADIO:1;
u8 __UNUSED:3,
   ENABLE_AM_FIX:1,
   ENABLE_BLMIN_TMP_OFF:1,
   ENABLE_RAW_DEMODULATORS:1,
   ENABLE_WIDE_RX:1,
   ENABLE_FLASHLIGHT:1;
} BUILD_OPTIONS;


// 0x0E80 EEPROM_DISP_CH_STORE_OFF
#seekto 0x2000;
u16 ScreenChannel_A;
u16 MrChannel_A;
u16 FreqChannel_A;
u16 ScreenChannel_B;
u16 MrChannel_B;
u16 FreqChannel_B;
u16 NoaaChannel_A;
u16 NoaaChannel_B;

// 0x0E70 EEPROM_SETTINGS_OFF
//#seekto 0x2010;
u16 call_channel;
u16 squelch;
u16 max_talk_time;
u16 noaa_autoscan;
u16 key_lock;
u16 vox_switch;
u16 vox_level;
u16 mic_gain;

// 0x0E70 EEPROM_SCANLIST_OFF
//#seekto 0x2020;
u16 slDef;
u16 sl1PriorEnab;
u16 sl1PriorCh1;
u16 sl1PriorCh2;
u16 sl2PriorEnab;
u16 sl2PriorCh1;
u16 sl2PriorCh2;
//u16 unused

// 0x0F50 EEPROM_MR_CH_NAME_OFF
#seekto 0x2030;
struct {
    char name[16];
// channels
} channelname[999];

// 0x0000 EEPROM_MR_CH_FREQ_OFF
// 0x0C80 EEPROM_FREQ_CH_FREQ_OFF
//#seekto 0x5ea0;
struct {
  ul32 freq;
  ul32 offset;

// 0x08
  u8 rxcode;
  u8 txcode;

// 0x0A
  u8 txcodeflag:4,
  rxcodeflag:4;

// 0x0B
  u8 modulation:4,
  shift:4;

// 0x0C
  u8 __UNUSED1:3,
  bclo:1,
  txpower:2,
  bandwidth:1,
  freq_reverse:1;

  // 0x0D
  u8 __UNUSED2:4,
  dtmf_pttid:3,
  dtmf_decode:1;

  // 0x0E
  u8 step;
  u8 scrambler;
// channels + 14
} channel[1013];

// 0x0D60 EEPROM_MR_CH_ATTR_OFF
// 0x0E28 EEPROM_FREQ_CH_ATTR_OFF
//#seekto 0x0df0;
struct {
  u8 is_scanlist1:1,
  is_scanlist2:1,
  compander:2,
  is_free:1,
   band:3;
// channels + 7
} channel_attributes[1006];
"""
# bits that we will save from the channel structure (mostly unknown)
SAVE_MASK_0A = 0b11001100
SAVE_MASK_0B = 0b11101100
SAVE_MASK_0C = 0b11100000
SAVE_MASK_0D = 0b11111000
SAVE_MASK_0E = 0b11110001
SAVE_MASK_0F = 0b11110000

# flags1
FLAGS1_OFFSET_NONE = 0b00
FLAGS1_OFFSET_MINUS = 0b10
FLAGS1_OFFSET_PLUS = 0b01

POWER_HIGH = 0b10
POWER_MEDIUM = 0b01
POWER_LOW = 0b00

# power
UVK5_POWER_LEVELS = [chirp_common.PowerLevel("Low",  watts=1.50),
                     chirp_common.PowerLevel("Med",  watts=3.00),
                     chirp_common.PowerLevel("High", watts=5.00),
                     ]

#ez scrambler
SCRAMBLER_LIST = ["Off", "2600Hz", "2700Hz", "2800Hz", "2900Hz", "3000Hz",
                  "3100Hz", "3200Hz", "3300Hz", "3400Hz", "3500Hz"]
# compander
COMPANDER_LIST = ["Off", "TX", "RX", "TX/RX"]

# rx mode
RXMODE_LIST = ["Main only", "Dual RX, respond", "Crossband",
               "Dual RX, TX on main"]
#ez channel display mode
CHANNELDISP_LIST = ["Frequency", "Channel Number", "Name", "Name + Frequency"]

# TalkTime
TALK_TIME_LIST = ["30 sec", "1 min", "2 min", "3 min", "4 min", "5 min",
                  "6 min", "7 min", "8 min", "9 min", "15 min"]

# battery save
BATSAVE_LIST = ["OFF", "1:1", "1:2", "1:3", "1:4"]
#ez battery type
BATTYPE_LIST = ["1600 mAh", "2200 mAh"]
#ez bat txt
BAT_TXT_LIST = ["None", "Voltage", "Percentage"]

#ez Backlight auto mode
BACKLIGHT_LIST = ["Off", "5s", "10s", "20s", "1min", "2min", "4min",
                  "Always On"]
#ez Backlight LVL
BACKLIGHT_LVL_LIST = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
#ez Backlight _TX_RX_LIST
BACKLIGHT_TX_RX_LIST = ["Off", "TX", "RX", "TX/RX"]

# Crossband receiving/transmitting
CROSSBAND_LIST = ["Off", "Band A", "Band B"]
DUALWATCH_LIST = CROSSBAND_LIST

# ctcss/dcs codes
TMODES = ["", "Tone", "DTCS", "DTCS"]
TONE_NONE = 0
TONE_CTCSS = 1
TONE_DCS = 2
TONE_RDCS = 3


CTCSS_TONES = [
    67.0, 69.3, 71.9, 74.4, 77.0, 79.7, 82.5, 85.4,
    88.5, 91.5, 94.8, 97.4, 100.0, 103.5, 107.2, 110.9,
    114.8, 118.8, 123.0, 127.3, 131.8, 136.5, 141.3, 146.2,
    151.4, 156.7, 159.8, 162.2, 165.5, 167.9, 171.3, 173.8,
    177.3, 179.9, 183.5, 186.2, 189.9, 192.8, 196.6, 199.5,
    203.5, 206.5, 210.7, 218.1, 225.7, 229.1, 233.6, 241.8,
    250.3, 254.1
]

# lifted from ft4.py
DTCS_CODES = [
    23,  25,  26,  31,  32,  36,  43,  47,  51,  53,  54,
    65,  71,  72,  73,  74,  114, 115, 116, 122, 125, 131,
    132, 134, 143, 145, 152, 155, 156, 162, 165, 172, 174,
    205, 212, 223, 225, 226, 243, 244, 245, 246, 251, 252,
    255, 261, 263, 265, 266, 271, 274, 306, 311, 315, 325,
    331, 332, 343, 346, 351, 356, 364, 365, 371, 411, 412,
    413, 423, 431, 432, 445, 446, 452, 454, 455, 462, 464,
    465, 466, 503, 506, 516, 523, 526, 532, 546, 565, 606,
    612, 624, 627, 631, 632, 654, 662, 664, 703, 712, 723,
    731, 732, 734, 743, 754
]

FLOCK_LIST = ["Off", "FCC", "CE", "GB", "430", "438"]

SCANRESUME_LIST = ["TO: Resume after 5 seconds",
                   "CO: Resume after signal disappears",
                   "SE: Stop scanning after receiving a signal"]

WELCOME_LIST = ["Full Screen", "Welcome Info", "Voltage"]
KEYPADTONE_LIST = ["Off", "Chinese", "English"]

LANGUAGE_LIST = ["Chinese", "English"]

ALARMMODE_LIST = ["SITE", "TONE"]
REMENDOFTALK_LIST = ["Off", "ROGER", "MDC"]
RTE_LIST = ["Off", "100ms", "200ms", "300ms", "400ms",
            "500ms", "600ms", "700ms", "800ms", "900ms"]

# flock list extended
FLOCK_LIST = ["Default+ (137-174, 400-470 + Tx200, Tx350, Tx500)",
              "FCC HAM (144-148, 420-450)",
              "CE HAM (144-146, 430-440)",
              "GB HAM (144-148, 430-440)",
              "137-174, 400-430",
              "137-174, 400-438",
              "Disable All",
              "Unlock All"]

SCANRESUME_LIST = ["Listen 5 seconds and resume",
                   "Listen until carrier disappears",
                   "Stop scanning after receiving a signal"]
WELCOME_LIST = ["Full screen test", "User message", "Battery voltage", "None"]
VOICE_LIST = ["Off", "Chinese", "English"]

# ACTIVE CHANNEL
TX_VFO_LIST = ["A", "B"]
ALARMMODE_LIST = ["Site", "Tone"]
ROGER_LIST = ["Off", "Roger beep", "MDC data burst"]
RTE_LIST = ["Off", "100ms", "200ms", "300ms", "400ms",
            "500ms", "600ms", "700ms", "800ms", "900ms", "1000ms"]
VOX_LIST = ["Off", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

# fm radio supported frequencies
FMMIN = 76.0
FMMAX = 108.0

# bands supported by the UV-K5
BANDS_STANDARD = {
        0: [50.0, 76.0],
        1: [108.0, 136.9999],
        2: [137.0, 173.9999],
        3: [174.0, 349.9999],
        4: [350.0, 399.9999],
        5: [400.0, 469.9999],
        6: [470.0, 600.0]
        }

BANDS_WIDE = {
        0: [18.0, 108.0],
        1: [108.0, 136.9999],
        2: [137.0, 173.9999],
        3: [174.0, 349.9999],
        4: [350.0, 399.9999],
        5: [400.0, 469.9999],
        6: [470.0, 1300.0]
        }

SCANLIST_SELECT_LIST = ["List 1", "List 2", "All channels"]

DTMF_CHARS = "0123456789ABCD*# "
DTMF_CHARS_ID = "0123456789ABCDabcd"
DTMF_CHARS_KILL = "0123456789ABCDabcd"
DTMF_CHARS_UPDOWN = "0123456789ABCDabcd#* "
DTMF_CODE_CHARS = "ABCD*# "
DTMF_DECODE_RESPONSE_LIST = ["Do nothing", "Local ringing", "Replay response",
                             "Local ringing + reply response"]

KEYACTIONS_LIST = ["None",
                   "Flashlight",
                   "TX power",
                   "Monitor",
                   "Scan",
                   "VOX",
                   "Alarm",
                   "FM broadcast radio",
                   "1750Hz tone",
                   "Lock keypad",
                   "Switch main VFO",
                   "Switch frequency/memory mode",
                   "Switch demodulation"
                   ]

MIC_GAIN_LIST = ["+1.1dB", "+4.0dB", "+8.0dB", "+12.0dB", "+15.1dB"]

MEM_SIZE = 0x2000  # size of all memory
PROG_SIZE = 0x1d00  # size of the memory that we will write
MEM_BLOCK = 0x80  # largest block of memory that we can reliably write

# fm radio supported frequencies
FMMIN = 76.0
FMMAX = 108.0

# bands supported by the UV-K5
BANDS = {
        0: [50.0, 76.0],
        1: [108.0, 135.9999],
        2: [136.0, 199.9990],
        3: [200.0, 299.9999],
        4: [350.0, 399.9999],
        5: [400.0, 469.9999],
        6: [470.0, 600.0]
        }

# for radios with modified firmware:
BANDS_NOLIMITS = {
        0: [18.0, 76.0],
        1: [108.0, 135.9999],
        2: [136.0, 199.9990],
        3: [200.0, 299.9999],
        4: [350.0, 399.9999],
        5: [400.0, 469.9999],
        6: [470.0, 1300.0]
        }

SPECIALS = {
        "F1(50M-76M)A": 200,
        "F1(50M-76M)B": 201,
        "F2(108M-136M)A": 202,
        "F2(108M-136M)B": 203,
        "F3(136M-174M)A": 204,
        "F3(136M-174M)B": 205,
        "F4(174M-350M)A": 206,
        "F4(174M-350M)B": 207,
        "F5(350M-400M)A": 208,
        "F5(350M-400M)B": 209,
        "F6(400M-470M)A": 210,
        "F6(400M-470M)B": 211,
        "F7(470M-600M)A": 212,
        "F7(470M-600M)B": 213
        }

VFO_CHANNEL_NAMES = ["F1(50M-76M)A", "F1(50M-76M)B",
                     "F2(108M-136M)A", "F2(108M-136M)B",
                     "F3(136M-174M)A", "F3(136M-174M)B",
                     "F4(174M-350M)A", "F4(174M-350M)B",
                     "F5(350M-400M)A", "F5(350M-400M)B",
                     "F6(400M-470M)A", "F6(400M-470M)B",
                     "F7(470M-600M)A", "F7(470M-600M)B"]

SCANLIST_LIST = ["None", "1", "2", "1+2"]


def xorarr(data: bytes):
    """the communication is obfuscated using this fine mechanism"""
    tbl = [22, 108, 20, 230, 46, 145, 13, 64, 33, 53, 213, 64, 19, 3, 233, 128]
    ret = b""
    idx = 0
    for byte in data:
        ret += bytes([byte ^ tbl[idx]])
        idx = (idx+1) % len(tbl)
    return ret


def calculate_crc16_xmodem(data: bytes):
    """
    if this crc was used for communication to AND from the radio, then it
    would be a measure to increase reliability.
    but it's only used towards the radio, so it's for further obfuscation
    """
    poly = 0x1021
    crc = 0x0
    for byte in data:
        crc = crc ^ (byte << 8)
        for _ in range(8):
            crc = crc << 1
            if crc & 0x10000:
                crc = (crc ^ poly) & 0xFFFF
    return crc & 0xFFFF


def _send_command(serport, data: bytes):
    """Send a command to UV-K5 radio"""
    LOG.debug("Sending command (unobfuscated) len=0x%4.4x:\n%s",
              len(data), util.hexprint(data))

    crc = calculate_crc16_xmodem(data)
    data2 = data + struct.pack("<H", crc)

    command = struct.pack(">HBB", 0xabcd, len(data), 0) + \
        xorarr(data2) + \
        struct.pack(">H", 0xdcba)
    if DEBUG_SHOW_OBFUSCATED_COMMANDS:
        LOG.debug("Sending command (obfuscated):\n%s", util.hexprint(command))
    try:
        result = serport.write(command)
    except Exception as e:
        raise errors.RadioError("Error writing data to radio") from e
    return result


def _receive_reply(serport):
    header = serport.read(4)
    if len(header) != 4:
        LOG.warning("Header short read: [%s] len=%i",
                    util.hexprint(header), len(header))
        raise errors.RadioError("Header short read")
    if header[0] != 0xAB or header[1] != 0xCD or header[3] != 0x00:
        LOG.warning("Bad response header: %s len=%i",
                    util.hexprint(header), len(header))
        raise errors.RadioError("Bad response header")

    cmd = serport.read(int(header[2]))
    if len(cmd) != int(header[2]):
        LOG.warning("Body short read: [%s] len=%i",
                    util.hexprint(cmd), len(cmd))
        raise errors.RadioError("Command body short read")

    footer = serport.read(4)

    if len(footer) != 4:
        LOG.warning("Footer short read: [%s] len=%i",
                    util.hexprint(footer), len(footer))
        raise errors.RadioError("Footer short read")

    if footer[2] != 0xDC or footer[3] != 0xBA:
        LOG.debug("Reply before bad response footer (obfuscated)"
                  "len=0x%4.4x:\n%s", len(cmd), util.hexprint(cmd))
        LOG.warning("Bad response footer: %s len=%i",
                    util.hexprint(footer), len(footer))
        raise errors.RadioError("Bad response footer")

    if DEBUG_SHOW_OBFUSCATED_COMMANDS:
        LOG.debug("Received reply (obfuscated) len=0x%4.4x:\n%s",
                  len(cmd), util.hexprint(cmd))

    cmd2 = xorarr(cmd)

    LOG.debug("Received reply (unobfuscated) len=0x%4.4x:\n%s",
              len(cmd2), util.hexprint(cmd2))

    return cmd2


def _getstring(data: bytes, begin, maxlen):
    tmplen = min(maxlen+1, len(data))
    ss = [data[i] for i in range(begin, tmplen)]
    key = 0
    for key, val in enumerate(ss):
        if val < ord(' ') or val > ord('~'):
            return ''.join(chr(x) for x in ss[0:key])
    return ''


def _sayhello(serport):
    hellopacket = b"\x14\x05\x04\x00\x6a\x39\x57\x64"

    tries = 5
    while True:
        LOG.debug("Sending hello packet")
        _send_command(serport, hellopacket)
        rep = _receive_reply(serport)
        if rep:
            break
        tries -= 1
        if tries == 0:
            LOG.warning("Failed to initialise radio")
            raise errors.RadioError("Failed to initialize radio")
    if rep.startswith(b'\x18\x05'):
        raise errors.RadioError("Radio is in programming mode, "
                                "restart radio into normal mode")
    firmware = _getstring(rep, 4, 24)

    LOG.info("Found firmware: %s", firmware)
    return firmware


def _readmem(serport, offset, length):
    LOG.debug("Sending readmem offset=0x%4.4x len=0x%4.4x", offset, length)

    readmem = b"\x1b\x05\x08\x00" + \
        struct.pack("<HBB", offset, length, 0) + \
        b"\x6a\x39\x57\x64"
    _send_command(serport, readmem)
    rep = _receive_reply(serport)
    if DEBUG_SHOW_MEMORY_ACTIONS:
        LOG.debug("readmem Received data len=0x%4.4x:\n%s",
                  len(rep), util.hexprint(rep))
    return rep[8:]


def _writemem(serport, data, offset):
    LOG.debug("Sending writemem offset=0x%4.4x len=0x%4.4x",
              offset, len(data))

    if DEBUG_SHOW_MEMORY_ACTIONS:
        LOG.debug("writemem sent data offset=0x%4.4x len=0x%4.4x:\n%s",
                  offset, len(data), util.hexprint(data))

    dlen = len(data)
    writemem = b"\x1d\x05" + \
        struct.pack("<BBHBB", dlen+8, 0, offset, dlen, 1) + \
        b"\x6a\x39\x57\x64"+data

    _send_command(serport, writemem)
    rep = _receive_reply(serport)

    LOG.debug("writemem Received data: %s len=%i",
              util.hexprint(rep), len(rep))

    if (rep[0] == 0x1e and
       rep[4] == (offset & 0xff) and
       rep[5] == (offset >> 8) & 0xff):
        return True

    LOG.warning("Bad data from writemem")
    raise errors.RadioError("Bad response to writemem")


def _resetradio(serport):
    resetpacket = b"\xdd\x05\x00\x00"
    _send_command(serport, resetpacket)


def do_download(radio):
    """download eeprom from radio"""
    serport = radio.pipe
    serport.timeout = 0.5
    status = chirp_common.Status()
    status.cur = 0
    status.max = radio._mem_size
    status.msg = "Downloading from radio"
    radio.status_fn(status)

    eeprom = b""
    f = _sayhello(serport)
    if not f:
        raise errors.RadioError('Unable to determine firmware version')

    if not radio.k5_approve_firmware(f):
        raise errors.RadioError(
            'Firmware version is not supported by this driver')

    radio.metadata = {'uvk5_firmware': f}

    addr = 0
    while addr < radio._mem_size:
        LOG.debug("Read address 0x%04x of 0x%04x blocksize 0x%02x",
                  addr, MEM_SIZE, MEM_BLOCK)
        data = _readmem(serport, addr, MEM_BLOCK)
        status.cur = addr
        radio.status_fn(status)

        if data and len(data) == MEM_BLOCK:
            eeprom += data
            addr += MEM_BLOCK
        else:
            raise errors.RadioError("Memory download incomplete")

    return memmap.MemoryMapBytes(eeprom)


def do_upload(radio):
    """upload configuration to radio eeprom"""
    serport = radio.pipe
    serport.timeout = 0.5
    status = chirp_common.Status()
    status.cur = 0
    status.msg = "Uploading to radio"

    if radio._upload_calibration:
        status.max = radio._cal_len
        start_addr = radio._cal_start
        stop_addr = radio._cal_end
        cal_start = radio._cal_start
        cal_len = 0
    else:
        status.max = radio._prog_size
        start_addr = 0
        stop_addr = radio._prog_size
        cal_start = radio._cal_start
        cal_len = radio._cal_end - radio._cal_start

    radio.status_fn(status)

    f = _sayhello(serport)
    if not f:
        raise errors.RadioError('Unable to determine firmware version')

    if not radio.k5_approve_firmware(f):
        raise errors.RadioError(
            'Firmware version is not supported by this driver')
    LOG.info('Uploading image from firmware %r to radio with %r',
             radio.metadata.get('uvk5_firmware', 'unknown'), f)
    addr = start_addr
    while addr < stop_addr:
        if addr == cal_start:
            if cal_len > 0:
                addr += cal_len
                LOG.info("Calibration section at 0x%04x length 0x%04x"
                         "- not written.", cal_start, cal_len)
                continue
        dat = radio.get_mmap()[addr:addr+MEM_BLOCK]
        _writemem(serport, dat, addr)
        status.cur = addr - start_addr
        radio.status_fn(status)
        if dat:
            addr += MEM_BLOCK
        else:
            raise errors.RadioError("Memory upload incomplete")
    status.msg = "Uploaded OK"

    _resetradio(serport)

    return True


def _find_band(nolimits, hz):
    mhz = hz/1000000.0
    if nolimits:
        B = BANDS_NOLIMITS
    else:
        B = BANDS

    # currently the hacked firmware sets band=1 below 50 MHz
    if nolimits and mhz < 50.0:
        return 1

    for a in B:
        if mhz >= B[a][0] and mhz <= B[a][1]:
            return a
    return False


class UVK5RadioBase(chirp_common.CloneModeRadio):
    """Quansheng UV-K5"""
    VENDOR = "Quansheng"
    MODEL = "UV-K5-egzumerLZ3ATZ"
    BAUD_RATE = 38400
    NEEDS_COMPAT_SERIAL = False
    _cal_start = 0x0000  # calibration memory start address
    _cal_end= 0x0000  # calibration memory end
    _cal_len = _cal_end - _cal_start  # calibration memory length
    _mem_size = MEM_SIZE # eeprom total size
    _prog_size = PROG_SIZE # eeprom size without calibration
    _channels = 200  # number of MR channels
    _channels_mask = 0xff  # max channel number
    _expanded_limits = False
    _upload_calibration = False
    _pttid_list = ["off", "BOT", "EOT", "BOTH"]
    _steps = [1.0, 2.5, 5.0, 6.25, 10.0, 12.5, 25.0, 8.33]

    @classmethod
    def k5_approve_firmware(cls, firmware):
        # All subclasses must implement this
        raise NotImplementedError()

    @classmethod
    def detect_from_serial(cls, pipe):
        firmware = _sayhello(pipe)
        for rclass in [UVK5Radio] + cls.DETECTED_MODELS:
            if rclass.k5_approve_firmware(firmware):
                return rclass
        raise errors.RadioError('Firmware %r not supported' % firmware)

    def get_prompts(x=None):
        rp = chirp_common.RadioPrompts()
        rp.experimental = _(
            'This is an experimental driver for the Quansheng UV-K5. '
            'It may harm your radio, or worse. Use at your own risk.\n\n'
            'Before attempting to do any changes please download '
            'the memory image from the radio with chirp '
            'and keep it. This can be later used to recover the '
            'original settings. \n\n'
            'some details are not yet implemented')
        rp.pre_download = _(
            "1. Turn radio on.\n"
            "2. Connect cable to mic/spkr connector.\n"
            "3. Make sure connector is firmly connected.\n"
            "4. Click OK to download image from device.\n\n"
            "It will may not work if you turn on the radio "
            "with the cable already attached\n")
        rp.pre_upload = _(
            "1. Turn radio on.\n"
            "2. Connect cable to mic/spkr connector.\n"
            "3. Make sure connector is firmly connected.\n"
            "4. Click OK to upload the image to device.\n\n"
            "It will may not work if you turn on the radio "
            "with the cable already attached")
        return rp

    # Return information about this radio's features, including
    # how many memories it has, what bands it supports, etc
    def get_features(self):
        rf = chirp_common.RadioFeatures()
        rf.has_bank = False
        rf.valid_dtcs_codes = DTCS_CODES
        rf.has_rx_dtcs = True
        rf.has_ctone = True
        rf.has_settings = True
        rf.has_comment = False
        rf.valid_name_length = 10
        rf.valid_power_levels = UVK5_POWER_LEVELS
        rf.valid_special_chans = list(SPECIALS.keys())
        rf.valid_duplexes = ["", "-", "+", "off"]

        # hack so we can input any frequency,
        # the 0.1 and 0.01 steps don't work unfortunately
        rf.valid_tuning_steps = list(self._steps)

        rf.valid_tmodes = ["", "Tone", "TSQL", "DTCS", "Cross"]
        rf.valid_cross_modes = ["Tone->Tone", "Tone->DTCS", "DTCS->Tone",
                                "->Tone", "->DTCS", "DTCS->", "DTCS->DTCS"]

        rf.valid_characters = chirp_common.CHARSET_ASCII
        rf.valid_modes = ["FM", "NFM", "AM", "NAM"]
        rf.valid_tmodes = ["", "Tone", "TSQL", "DTCS", "Cross"]

        rf.valid_skips = [""]

        # This radio supports memories 1-200, 201-214 are the VFO memories
        rf.memory_bounds = (1, self._channels)

        rf.valid_bands = []
        for a in BANDS_NOLIMITS:
            rf.valid_bands.append(
                    (int(BANDS_NOLIMITS[a][0]*1000000),
                     int(BANDS_NOLIMITS[a][1]*1000000)))
        return rf

    # Do a download of the radio from the serial port
    def sync_in(self):
        self._mmap = do_download(self)
        self.process_mmap()

    # Do an upload of the radio to the serial port
    def sync_out(self):
        do_upload(self)

    def _check_firmware_at_load(self):
        firmware = self.metadata.get('uvk5_firmware')
        if not firmware:
            LOG.warning(_('This image is missing firmware information. '
                          'It may have been generated with an old or '
                          'modified version of CHIRP. It is advised that '
                          'you download a fresh image from your radio and '
                          'use that going forward for the best safety and '
                          'compatibility.'))
        elif not self.k5_approve_firmware(self.metadata['uvk5_firmware']):
            raise errors.RadioError(
                'Image firmware is %r but is not supported by '
                'this driver' % firmware)

    # Convert the raw byte array into a memory object structure
    def process_mmap(self):
        self._check_firmware_at_load()
        self._memobj = bitwise.parse(MEM_FORMAT, self._mmap)

    # Return a raw representation of the memory object, which
    # is very helpful for development
    def get_raw_memory(self, number):
        return repr(self._memobj.channel[number-1])

    def validate_memory(self, mem):
        msgs = super().validate_memory(mem)

        if mem.duplex == 'off':
            return msgs

        # find tx frequency
        if mem.duplex == '-':
            txfreq = mem.freq - mem.offset
        elif mem.duplex == '+':
            txfreq = mem.freq + mem.offset
        else:
            txfreq = mem.freq

        # find band
        band = _find_band(self._expanded_limits, txfreq)
        if band is False:
            msg = "Transmit frequency %.4f MHz is not supported by this radio"\
                   % (txfreq/1000000.0)
            msgs.append(chirp_common.ValidationError(msg))

        band = _find_band(self._expanded_limits, mem.freq)
        if band is False:
            msg = "The frequency %.4f MHz is not supported by this radio" \
                   % (mem.freq/1000000.0)
            msgs.append(chirp_common.ValidationError(msg))

        return msgs

    def _set_tone(self, mem, _mem):
        ((txmode, txtone, txpol),
         (rxmode, rxtone, rxpol)) = chirp_common.split_tone_encode(mem)

        if txmode == "Tone":
            txtoval = CTCSS_TONES.index(txtone)
            txmoval = 0b01
        elif txmode == "DTCS":
            txmoval = txpol == "R" and 0b11 or 0b10
            txtoval = DTCS_CODES.index(txtone)
        else:
            txmoval = 0
            txtoval = 0

        if rxmode == "Tone":
            rxtoval = CTCSS_TONES.index(rxtone)
            rxmoval = 0b01
        elif rxmode == "DTCS":
            rxmoval = rxpol == "R" and 0b11 or 0b10
            rxtoval = DTCS_CODES.index(rxtone)
        else:
            rxmoval = 0
            rxtoval = 0

        _mem.rxcodeflag = rxmoval
        _mem.txcodeflag = txmoval
        _mem.rxcode = rxtoval
        _mem.txcode = txtoval

    def _get_tone(self, mem, _mem):
        rxtype = _mem.rxcodeflag
        txtype = _mem.txcodeflag
        rx_tmode = TMODES[rxtype]
        tx_tmode = TMODES[txtype]

        rx_tone = tx_tone = None

        if tx_tmode == "Tone":
            if _mem.txcode < len(CTCSS_TONES):
                tx_tone = CTCSS_TONES[_mem.txcode]
            else:
                tx_tone = 0
                tx_tmode = ""
        elif tx_tmode == "DTCS":
            if _mem.txcode < len(DTCS_CODES):
                tx_tone = DTCS_CODES[_mem.txcode]
            else:
                tx_tone = 0
                tx_tmode = ""

        if rx_tmode == "Tone":
            if _mem.rxcode < len(CTCSS_TONES):
                rx_tone = CTCSS_TONES[_mem.rxcode]
            else:
                rx_tone = 0
                rx_tmode = ""
        elif rx_tmode == "DTCS":
            if _mem.rxcode < len(DTCS_CODES):
                rx_tone = DTCS_CODES[_mem.rxcode]
            else:
                rx_tone = 0
                rx_tmode = ""

        tx_pol = txtype == 0x03 and "R" or "N"
        rx_pol = rxtype == 0x03 and "R" or "N"

        chirp_common.split_tone_decode(mem, (tx_tmode, tx_tone, tx_pol),
                                       (rx_tmode, rx_tone, rx_pol))

    def _get_mem_extra(self, mem, _mem):
        tmpscn = SCANLIST_LIST[0]

        # We'll also look at the channel attributes if a memory has them
        if mem.number <= self._channels:
            _mem3 = self._memobj.channel_attributes[mem.number - 1]
            # free memory bit
            if _mem3.is_free > 0:
                mem.empty = True
            # scanlists
            if _mem3.is_scanlist1 > 0 and _mem3.is_scanlist2 > 0:
                tmpscn = SCANLIST_LIST[3]  # "1+2"
            elif _mem3.is_scanlist1 > 0:
                tmpscn = SCANLIST_LIST[1]  # "1"
            elif _mem3.is_scanlist2 > 0:
                tmpscn = SCANLIST_LIST[2]  # "2"

        mem.extra = RadioSettingGroup("Extra", "extra")

        # BCLO
        is_bclo = bool(_mem.bclo > 0)
        rs = RadioSetting("bclo", "BCLO", RadioSettingValueBoolean(is_bclo))
        mem.extra.append(rs)

        # Frequency reverse - whatever that means, don't see it in the manual
        is_frev = bool(_mem.freq_reverse > 0)
        rs = RadioSetting("frev", "FreqRev", RadioSettingValueBoolean(is_frev))
        mem.extra.append(rs)

        # PTTID
        try:
            pttid = self._pttid_list[_mem.dtmf_pttid]
        except IndexError:
            pttid = 0
        rs = RadioSetting("pttid", "PTTID", RadioSettingValueList(
            self._pttid_list, pttid))
        mem.extra.append(rs)

        # DTMF DECODE
        is_dtmf = bool(_mem.dtmf_decode > 0)
        rs = RadioSetting("dtmfdecode", _("DTMF decode"),
                          RadioSettingValueBoolean(is_dtmf))
        mem.extra.append(rs)

        # Scrambler
        if _mem.scrambler & 0x0f < len(SCRAMBLER_LIST):
            enc = _mem.scrambler & 0x0f
        else:
            enc = 0

        rs = RadioSetting("scrambler", _("Scrambler"), RadioSettingValueList(
            SCRAMBLER_LIST, SCRAMBLER_LIST[enc]))
        mem.extra.append(rs)

        rs = RadioSetting("scanlists", _("Scanlists"), RadioSettingValueList(
            SCANLIST_LIST, tmpscn))
        mem.extra.append(rs)

    def _get_mem_mode(self, _mem):
        if _mem.enable_am > 0:
            if _mem.bandwidth > 0:
                return "NAM"
            else:
                return "AM"
        else:
            if _mem.bandwidth > 0:
                return "NFM"
            else:
                return "FM"

    def _get_specials(self):
        return dict(SPECIALS)

    # Extract a high-level memory object from the low-level memory map
    # This is called to populate a memory in the UI
    def get_memory(self, number2):

        mem = chirp_common.Memory()

        if isinstance(number2, str):
            number = self._get_specials()[number2]
            mem.extd_number = number2
        else:
            number = number2 - 1

        mem.number = number + 1

        _mem = self._memobj.channel[number]

        # We'll consider any blank (i.e. 0 MHz frequency) to be empty
        if (_mem.freq == 0xffffffff) or (_mem.freq == 0):
            mem.empty = True

        self._get_mem_extra(mem, _mem)

        if mem.empty:
            return mem

        if number > self._channels - 1:
            mem.immutable = ["name", "scanlists"]
        else:
            _mem2 = self._memobj.channelname[number]
            for char in _mem2.name:
                if str(char) == "\xFF" or str(char) == "\x00":
                    break
                mem.name += str(char)
            mem.name = mem.name.rstrip()

        # Convert your low-level frequency to Hertz
        mem.freq = int(_mem.freq)*10
        mem.offset = int(_mem.offset)*10

        if (mem.offset == 0):
            mem.duplex = ''
        else:
            if _mem.shift == FLAGS1_OFFSET_MINUS:
                if _mem.freq == _mem.offset:
                    # fake tx disable by setting tx to 0 MHz
                    mem.duplex = 'off'
                    mem.offset = 0
                else:
                    mem.duplex = '-'
            elif _mem.shift == FLAGS1_OFFSET_PLUS:
                mem.duplex = '+'
            else:
                mem.duplex = ''

        # tone data
        self._get_tone(mem, _mem)

        mem.mode = self._get_mem_mode(_mem)

        # tuning step
        try:
            mem.tuning_step = self._steps[_mem.step]
        except IndexError:
            mem.tuning_step = 2.5

        # power
        if _mem.txpower == POWER_HIGH:
            mem.power = UVK5_POWER_LEVELS[2]
        elif _mem.txpower == POWER_MEDIUM:
            mem.power = UVK5_POWER_LEVELS[1]
        else:
            mem.power = UVK5_POWER_LEVELS[0]

        # We'll consider any blank (i.e. 0 MHz frequency) to be empty
        if (_mem.freq == 0xffffffff) or (_mem.freq == 0):
            mem.empty = True
        else:
            mem.empty = False

        return mem

    def set_settings(self, settings):
        _mem = self._memobj
        for element in settings:
            if not isinstance(element, RadioSetting):
                self.set_settings(element)
                continue

            # basic settings

            # call channel
            if element.get_name() == "call_channel":
                _mem.call_channel = int(element.value)-1

            # squelch
            if element.get_name() == "squelch":
                _mem.squelch = int(element.value)
            # TOT
            if element.get_name() == "tot":
                _mem.max_talk_time = int(element.value)

            # NOAA autoscan
            if element.get_name() == "noaa_autoscan":
                _mem.noaa_autoscan = element.value and 1 or 0

            # VOX switch
            if element.get_name() == "vox_switch":
                _mem.vox_switch = element.value and 1 or 0

            # vox level
            if element.get_name() == "vox_level":
                _mem.vox_level = int(element.value)-1

            # mic gain
            if element.get_name() == "mic_gain":
                _mem.mic_gain = int(element.value)

            # Channel display mode
            if element.get_name() == "channel_display_mode":
                _mem.channel_display_mode = CHANNELDISP_LIST.index(
                    str(element.value))

            # Crossband receiving/transmitting
            if element.get_name() == "crossband":
                _mem.crossband = CROSSBAND_LIST.index(str(element.value))

            # Battery Save
            if element.get_name() == "battery_save":
                _mem.battery_save = BATSAVE_LIST.index(str(element.value))
            # Dual Watch
            if element.get_name() == "dualwatch":
                _mem.dual_watch = DUALWATCH_LIST.index(str(element.value))

            # Backlight auto mode
            if element.get_name() == "backlight_auto_mode":
                _mem.backlight_auto_mode = \
                        BACKLIGHT_LIST.index(str(element.value))

            # Tail tone elimination
            if element.get_name() == "tail_note_elimination":
                _mem.tail_note_elimination = element.value and 1 or 0

            # VFO Open
            if element.get_name() == "vfo_open":
                _mem.vfo_open = element.value and 1 or 0

            # Beep control
            if element.get_name() == "beep_control":
                _mem.beep_control = element.value and 1 or 0

            # Scan resume mode
            if element.get_name() == "scan_resume_mode":
                _mem.scan_resume_mode = SCANRESUME_LIST.index(
                    str(element.value))

            # Keypad lock
            if element.get_name() == "key_lock":
                _mem.key_lock = element.value and 1 or 0

            # Auto keypad lock
            if element.get_name() == "auto_keypad_lock":
                _mem.auto_keypad_lock = element.value and 1 or 0

            # Power on display mode
            if element.get_name() == "welcome_mode":
                _mem.power_on_dispmode = WELCOME_LIST.index(str(element.value))

            # Keypad Tone
            if element.get_name() == "keypad_tone":
                _mem.keypad_tone = KEYPADTONE_LIST.index(str(element.value))

            # Language
            if element.get_name() == "language":
                _mem.language = LANGUAGE_LIST.index(str(element.value))

            # Alarm mode
            if element.get_name() == "alarm_mode":
                _mem.alarm_mode = ALARMMODE_LIST.index(str(element.value))

            # Reminding of end of talk
            if element.get_name() == "reminding_of_end_talk":
                _mem.reminding_of_end_talk = REMENDOFTALK_LIST.index(
                    str(element.value))

            # Repeater tail tone elimination
            if element.get_name() == "repeater_tail_elimination":
                _mem.repeater_tail_elimination = RTE_LIST.index(
                    str(element.value))

            # Logo string 1
            if element.get_name() == "logo1":
                b = str(element.value).rstrip("\x20\xff\x00")+"\x00"*12
                _mem.logo_line1 = b[0:12]+"\x00\xff\xff\xff"

            # Logo string 2
            if element.get_name() == "logo2":
                b = str(element.value).rstrip("\x20\xff\x00")+"\x00"*12
                _mem.logo_line2 = b[0:12]+"\x00\xff\xff\xff"

            # unlock settings

            # FLOCK
            if element.get_name() == "flock":
                _mem.lock.flock = FLOCK_LIST.index(str(element.value))

            # 350TX
            if element.get_name() == "tx350":
                _mem.lock.tx350 = element.value and 1 or 0

            # 200TX
            if element.get_name() == "tx200":
                _mem.lock.tx200 = element.value and 1 or 0

            # 500TX
            if element.get_name() == "tx500":
                _mem.lock.tx500 = element.value and 1 or 0

            # 350EN
            if element.get_name() == "en350":
                _mem.lock.en350 = element.value and 1 or 0

            # SCREN
            if element.get_name() == "enscramble":
                _mem.lock.enscramble = element.value and 1 or 0

            # KILLED
            if element.get_name() == "killed":
                _mem.lock.killed = element.value and 1 or 0

            # fm radio
            for i in range(1, 21):
                freqname = "FM_" + str(i)
                if element.get_name() == freqname:
                    val = str(element.value).strip()
                    try:
                        val2 = int(float(val)*10)
                    except Exception:
                        val2 = 0xffff

                    if val2 < FMMIN*10 or val2 > FMMAX*10:
                        val2 = 0xffff
#                        raise errors.InvalidValueError(
#                                "FM radio frequency should be a value "
#                                "in the range %.1f - %.1f" % (FMMIN , FMMAX))
                    _mem.fmfreq[i-1] = val2

            # dtmf settings
            if element.get_name() == "dtmf_side_tone":
                _mem.dtmf_settings.side_tone = \
                        element.value and 1 or 0

            if element.get_name() == "dtmf_separate_code":
                _mem.dtmf_settings.separate_code = str(element.value)

            if element.get_name() == "dtmf_group_call_code":
                _mem.dtmf_settings.group_call_code = element.value

            if element.get_name() == "dtmf_decode_response":
                _mem.dtmf_settings.decode_response = \
                        DTMF_DECODE_RESPONSE_LIST.index(str(element.value))

            if element.get_name() == "dtmf_auto_reset_time":
                _mem.dtmf_settings.auto_reset_time = \
                        int(int(element.value)/10)

            if element.get_name() == "dtmf_preload_time":
                _mem.dtmf_settings.preload_time = \
                        int(int(element.value)/10)

            if element.get_name() == "dtmf_first_code_persist_time":
                _mem.dtmf_settings.first_code_persist_time = \
                        int(int(element.value)/10)

            if element.get_name() == "dtmf_hash_persist_time":
                _mem.dtmf_settings.hash_persist_time = \
                        int(int(element.value)/10)

            if element.get_name() == "dtmf_code_persist_time":
                _mem.dtmf_settings.code_persist_time = \
                        int(int(element.value)/10)

            if element.get_name() == "dtmf_code_interval_time":
                _mem.dtmf_settings.code_interval_time = \
                        int(int(element.value)/10)

            if element.get_name() == "dtmf_permit_remote_kill":
                _mem.dtmf_settings.permit_remote_kill = \
                        element.value and 1 or 0

            if element.get_name() == "dtmf_dtmf_local_code":
                k = str(element.value).rstrip("\x20\xff\x00") + "\x00"*3
                _mem.dtmf_settings_numbers.dtmf_local_code = k[0:3]

            if element.get_name() == "dtmf_dtmf_up_code":
                k = str(element.value).strip("\x20\xff\x00") + "\x00"*16
                _mem.dtmf_settings_numbers.dtmf_up_code = k[0:16]

            if element.get_name() == "dtmf_dtmf_down_code":
                k = str(element.value).rstrip("\x20\xff\x00") + "\x00"*16
                _mem.dtmf_settings_numbers.dtmf_down_code = k[0:16]

            if element.get_name() == "dtmf_kill_code":
                k = str(element.value).strip("\x20\xff\x00") + "\x00"*5
                _mem.dtmf_settings_numbers.kill_code = k[0:5]

            if element.get_name() == "dtmf_revive_code":
                k = str(element.value).strip("\x20\xff\x00") + "\x00"*5
                _mem.dtmf_settings_numbers.revive_code = k[0:5]

            # dtmf contacts
            for i in range(1, 17):
                varname = "DTMF_" + str(i)
                if element.get_name() == varname:
                    k = str(element.value).rstrip("\x20\xff\x00") + "\x00"*8
                    _mem.dtmfcontact[i-1].name = k[0:8]

                varnumname = "DTMFNUM_" + str(i)
                if element.get_name() == varnumname:
                    k = str(element.value).rstrip("\x20\xff\x00") + "\xff"*3
                    _mem.dtmfcontact[i-1].number = k[0:3]

            # scanlist stuff
            if element.get_name() == "scanlist_default":
                val = (int(element.value) == 2) and 1 or 0
                _mem.scanlist_default = val

            if element.get_name() == "scanlist1_priority_scan":
                _mem.scanlist1_priority_scan = \
                        element.value and 1 or 0

            if element.get_name() == "scanlist2_priority_scan":
                _mem.scanlist2_priority_scan = \
                        element.value and 1 or 0

            if element.get_name() == "scanlist1_priority_ch1" or \
                    element.get_name() == "scanlist1_priority_ch2" or \
                    element.get_name() == "scanlist2_priority_ch1" or \
                    element.get_name() == "scanlist2_priority_ch2":

                val = int(element.value)

                if val > self._channels or val < 1:
                    val = self._channels_mask
                else:
                    val -= 1

                if element.get_name() == "scanlist1_priority_ch1":
                    _mem.scanlist1_priority_ch1 = val
                if element.get_name() == "scanlist1_priority_ch2":
                    _mem.scanlist1_priority_ch2 = val
                if element.get_name() == "scanlist2_priority_ch1":
                    _mem.scanlist2_priority_ch1 = val
                if element.get_name() == "scanlist2_priority_ch2":
                    _mem.scanlist2_priority_ch2 = val

            if element.get_name() == "key1_shortpress_action":
                _mem.key1_shortpress_action = KEYACTIONS_LIST.index(
                        str(element.value))

            if element.get_name() == "key1_longpress_action":
                _mem.key1_longpress_action = KEYACTIONS_LIST.index(
                        str(element.value))

            if element.get_name() == "key2_shortpress_action":
                _mem.key2_shortpress_action = KEYACTIONS_LIST.index(
                        str(element.value))

            if element.get_name() == "key2_longpress_action":
                _mem.key2_longpress_action = KEYACTIONS_LIST.index(
                        str(element.value))

            if element.get_name() == "nolimits":
                LOG.warning("User expanded band limits")
                self._expanded_limits = bool(element.value)

    def get_settings(self):
        _mem = self._memobj
        basic = RadioSettingGroup("basic", "Basic Settings")
        keya = RadioSettingGroup("keya", "Programmable keys")
        dtmf = RadioSettingGroup("dtmf", "DTMF Settings")
        dtmfc = RadioSettingGroup("dtmfc", "DTMF Contacts")
        scanl = RadioSettingGroup("scn", "Scan Lists")
        unlock = RadioSettingGroup("unlock", "Unlock Settings")
        fmradio = RadioSettingGroup("fmradio", _("FM Radio"))

        roinfo = RadioSettingGroup("roinfo", _("Driver information"))

        top = RadioSettings(
                basic, keya, dtmf, dtmfc, scanl, unlock, fmradio, roinfo)

        # Programmable keys
        tmpval = int(_mem.key1_shortpress_action)
        if tmpval >= len(KEYACTIONS_LIST):
            tmpval = 0
        rs = RadioSetting("key1_shortpress_action", "Side key 1 short press",
                          RadioSettingValueList(
                              KEYACTIONS_LIST, KEYACTIONS_LIST[tmpval]))
        keya.append(rs)

        tmpval = int(_mem.key1_longpress_action)
        if tmpval >= len(KEYACTIONS_LIST):
            tmpval = 0
        rs = RadioSetting("key1_longpress_action", "Side key 1 long press",
                          RadioSettingValueList(
                              KEYACTIONS_LIST, KEYACTIONS_LIST[tmpval]))
        keya.append(rs)

        tmpval = int(_mem.key2_shortpress_action)
        if tmpval >= len(KEYACTIONS_LIST):
            tmpval = 0
        rs = RadioSetting("key2_shortpress_action", "Side key 2 short press",
                          RadioSettingValueList(
                              KEYACTIONS_LIST, KEYACTIONS_LIST[tmpval]))
        keya.append(rs)

        tmpval = int(_mem.key2_longpress_action)
        if tmpval >= len(KEYACTIONS_LIST):
            tmpval = 0
        rs = RadioSetting("key2_longpress_action", "Side key 2 long press",
                          RadioSettingValueList(
                              KEYACTIONS_LIST, KEYACTIONS_LIST[tmpval]))
        keya.append(rs)

        # DTMF settings
        tmppr = bool(_mem.dtmf_settings.side_tone > 0)
        rs = RadioSetting(
                "dtmf_side_tone",
                "DTMF Sidetone",
                RadioSettingValueBoolean(tmppr))
        dtmf.append(rs)

        tmpval = str(_mem.dtmf_settings.separate_code)
        if tmpval not in DTMF_CODE_CHARS:
            tmpval = '*'
        val = RadioSettingValueString(1, 1, tmpval)
        val.set_charset(DTMF_CODE_CHARS)
        rs = RadioSetting("dtmf_separate_code", "Separate Code", val)
        dtmf.append(rs)

        tmpval = str(_mem.dtmf_settings.group_call_code)
        if tmpval not in DTMF_CODE_CHARS:
            tmpval = '#'
        val = RadioSettingValueString(1, 1, tmpval)
        val.set_charset(DTMF_CODE_CHARS)
        rs = RadioSetting("dtmf_group_call_code", "Group Call Code", val)
        dtmf.append(rs)

        tmpval = _mem.dtmf_settings.decode_response
        if tmpval >= len(DTMF_DECODE_RESPONSE_LIST):
            tmpval = 0
        rs = RadioSetting("dtmf_decode_response", "Decode Response",
                          RadioSettingValueList(
                              DTMF_DECODE_RESPONSE_LIST,
                              DTMF_DECODE_RESPONSE_LIST[tmpval]))
        dtmf.append(rs)

        tmpval = _mem.dtmf_settings.auto_reset_time
        if tmpval > 60 or tmpval < 5:
            tmpval = 5
        rs = RadioSetting("dtmf_auto_reset_time",
                          "Auto reset time (s)",
                          RadioSettingValueInteger(5, 60, tmpval))
        dtmf.append(rs)

        tmpval = int(_mem.dtmf_settings.preload_time)
        if tmpval > 100 or tmpval < 3:
            tmpval = 30
        tmpval *= 10
        rs = RadioSetting("dtmf_preload_time",
                          "Pre-load time (ms)",
                          RadioSettingValueInteger(30, 1000, tmpval, 10))
        dtmf.append(rs)

        tmpval = int(_mem.dtmf_settings.first_code_persist_time)
        if tmpval > 100 or tmpval < 3:
            tmpval = 30
        tmpval *= 10
        rs = RadioSetting("dtmf_first_code_persist_time",
                          "First code persist time (ms)",
                          RadioSettingValueInteger(30, 1000, tmpval, 10))
        dtmf.append(rs)

        tmpval = int(_mem.dtmf_settings.hash_persist_time)
        if tmpval > 100 or tmpval < 3:
            tmpval = 30
        tmpval *= 10
        rs = RadioSetting("dtmf_hash_persist_time",
                          "#/* persist time (ms)",
                          RadioSettingValueInteger(30, 1000, tmpval, 10))
        dtmf.append(rs)

        tmpval = int(_mem.dtmf_settings.code_persist_time)
        if tmpval > 100 or tmpval < 3:
            tmpval = 30
        tmpval *= 10
        rs = RadioSetting("dtmf_code_persist_time",
                          "Code persist time (ms)",
                          RadioSettingValueInteger(30, 1000, tmpval, 10))
        dtmf.append(rs)

        tmpval = int(_mem.dtmf_settings.code_interval_time)
        if tmpval > 100 or tmpval < 3:
            tmpval = 30
        tmpval *= 10
        rs = RadioSetting("dtmf_code_interval_time",
                          "Code interval time (ms)",
                          RadioSettingValueInteger(30, 1000, tmpval, 10))
        dtmf.append(rs)

        tmpval = bool(_mem.dtmf_settings.permit_remote_kill > 0)
        rs = RadioSetting(
                "dtmf_permit_remote_kill",
                "Permit remote kill",
                RadioSettingValueBoolean(tmpval))
        dtmf.append(rs)

        tmpval = str(_mem.dtmf_settings_numbers.dtmf_local_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_ID:
                continue
            else:
                tmpval = "103"
                break
        val = RadioSettingValueString(3, 3, tmpval)
        val.set_charset(DTMF_CHARS_ID)
        rs = RadioSetting("dtmf_dtmf_local_code",
                          "Local code (3 chars 0-9 ABCD)", val)
        dtmf.append(rs)

        tmpval = str(_mem.dtmf_settings_numbers.dtmf_up_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_UPDOWN or i == "":
                continue
            else:
                tmpval = "123"
                break
        val = RadioSettingValueString(1, 16, tmpval)
        val.set_charset(DTMF_CHARS_UPDOWN)
        rs = RadioSetting("dtmf_dtmf_up_code",
                          "Up code (1-16 chars 0-9 ABCD*#)", val)
        dtmf.append(rs)

        tmpval = str(_mem.dtmf_settings_numbers.dtmf_down_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_UPDOWN:
                continue
            else:
                tmpval = "456"
                break
        val = RadioSettingValueString(1, 16, tmpval)
        val.set_charset(DTMF_CHARS_UPDOWN)
        rs = RadioSetting("dtmf_dtmf_down_code",
                          "Down code (1-16 chars 0-9 ABCD*#)", val)
        dtmf.append(rs)

        tmpval = str(_mem.dtmf_settings_numbers.kill_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_KILL:
                continue
            else:
                tmpval = "77777"
                break
        if not len(tmpval) == 5:
            tmpval = "77777"
        val = RadioSettingValueString(5, 5, tmpval)
        val.set_charset(DTMF_CHARS_KILL)
        rs = RadioSetting("dtmf_kill_code",
                          "Kill code (5 chars 0-9 ABCD)", val)
        dtmf.append(rs)

        tmpval = str(_mem.dtmf_settings_numbers.revive_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_KILL:
                continue
            else:
                tmpval = "88888"
                break
        if not len(tmpval) == 5:
            tmpval = "88888"
        val = RadioSettingValueString(5, 5, tmpval)
        val.set_charset(DTMF_CHARS_KILL)
        rs = RadioSetting("dtmf_revive_code",
                          "Revive code (5 chars 0-9 ABCD)", val)
        dtmf.append(rs)

        for i in range(1, 17):
            varname = "DTMF_"+str(i)
            varnumname = "DTMFNUM_"+str(i)
            vardescr = "DTMF Contact "+str(i)+" name"
            varinumdescr = "DTMF Contact "+str(i)+" number"

            cntn = str(_mem.dtmfcontact[i-1].name).strip("\x20\x00\xff")
            cntnum = str(_mem.dtmfcontact[i-1].number).strip("\x20\x00\xff")

            val = RadioSettingValueString(0, 8, cntn)
            rs = RadioSetting(varname, vardescr, val)
            dtmfc.append(rs)

            val = RadioSettingValueString(0, 3, cntnum)
            val.set_charset(DTMF_CHARS)
            rs = RadioSetting(varnumname, varinumdescr, val)
            dtmfc.append(rs)
            rs.set_doc("DTMF Contacts are 3 codes (valid: 0-9 * # ABCD), "
                       "or an empty string")

        # scanlists
        if _mem.scanlist_default == 1:
            tmpsc = 2
        else:
            tmpsc = 1
        rs = RadioSetting("scanlist_default",
                          "Default scanlist",
                          RadioSettingValueInteger(1, 2, tmpsc))
        scanl.append(rs)

        tmppr = bool((_mem.scanlist1_priority_scan & 1) > 0)
        rs = RadioSetting(
                "scanlist1_priority_scan",
                "Scanlist 1 priority channel scan",
                RadioSettingValueBoolean(tmppr))
        scanl.append(rs)

        tmpch = _mem.scanlist1_priority_ch1 + 1
        if tmpch > self._channels:
            tmpch = 0
        rs = RadioSetting("scanlist1_priority_ch1",
                          "Scanlist 1 priority channel 1 (0 - off)",
                          RadioSettingValueInteger(0, self._channels, tmpch))
        scanl.append(rs)

        tmpch = _mem.scanlist1_priority_ch2 + 1
        if tmpch > self._channels:
            tmpch = 0
        rs = RadioSetting("scanlist1_priority_ch2",
                          "Scanlist 1 priority channel 2 (0 - off)",
                          RadioSettingValueInteger(0, self._channels, tmpch))
        scanl.append(rs)

        tmppr = bool((_mem.scanlist2_priority_scan & 1) > 0)
        rs = RadioSetting(
                "scanlist2_priority_scan",
                "Scanlist 2 priority channel scan",
                RadioSettingValueBoolean(tmppr))
        scanl.append(rs)

        tmpch = _mem.scanlist2_priority_ch1 + 1
        if tmpch > self._channels:
            tmpch = 0
        rs = RadioSetting("scanlist2_priority_ch1",
                          "Scanlist 2 priority channel 1 (0 - off)",
                          RadioSettingValueInteger(0, self._channels, tmpch))
        scanl.append(rs)

        tmpch = _mem.scanlist2_priority_ch2 + 1
        if tmpch > self._channels:
            tmpch = 0
        rs = RadioSetting("scanlist2_priority_ch2",
                          "Scanlist 2 priority channel 2 (0 - off)",
                          RadioSettingValueInteger(0, self._channels, tmpch))
        scanl.append(rs)

        # basic settings

        # call channel
        tmpc = _mem.call_channel+1
        if tmpc > self._channels:
            tmpc = 1
        rs = RadioSetting("call_channel", "One key call channel",
                          RadioSettingValueInteger(1, self._channels, tmpc))
        basic.append(rs)

        # squelch
        tmpsq = _mem.squelch
        if tmpsq > 9:
            tmpsq = 1
        rs = RadioSetting("squelch", "Squelch",
                          RadioSettingValueInteger(0, 9, tmpsq))
        basic.append(rs)

        # TOT
        tmptot = _mem.max_talk_time
        if tmptot > 10:
            tmptot = 10
        rs = RadioSetting(
                "tot",
                "Max talk time [min]",
                RadioSettingValueInteger(0, 10, tmptot))
        basic.append(rs)

        # NOAA autoscan
        rs = RadioSetting(
                "noaa_autoscan",
                "NOAA Autoscan", RadioSettingValueBoolean(
                    bool(_mem.noaa_autoscan > 0)))
        basic.append(rs)

        # VOX switch
        rs = RadioSetting(
                "vox_switch",
                "VOX enabled", RadioSettingValueBoolean(
                    bool(_mem.vox_switch > 0)))
        basic.append(rs)

        # VOX Level
        tmpvox = _mem.vox_level+1
        if tmpvox > 10:
            tmpvox = 10
        rs = RadioSetting("vox_level", "VOX Level",
                          RadioSettingValueInteger(1, 10, tmpvox))
        basic.append(rs)

        # Mic gain
        tmpmicgain = _mem.mic_gain
        if tmpmicgain > 4:
            tmpmicgain = 4
        rs = RadioSetting("mic_gain", "Mic Gain",
                          RadioSettingValueInteger(0, 4, tmpmicgain))
        basic.append(rs)

        # Channel display mode
        tmpchdispmode = _mem.channel_display_mode
        if tmpchdispmode >= len(CHANNELDISP_LIST):
            tmpchdispmode = 0
        rs = RadioSetting(
                "channel_display_mode",
                "Channel display mode",
                RadioSettingValueList(
                    CHANNELDISP_LIST,
                    CHANNELDISP_LIST[tmpchdispmode]))
        basic.append(rs)

        # Crossband receiving/transmitting
        tmpcross = _mem.crossband
        if tmpcross >= len(CROSSBAND_LIST):
            tmpcross = 0
        rs = RadioSetting(
                "crossband",
                "Cross-band receiving/transmitting",
                RadioSettingValueList(
                    CROSSBAND_LIST,
                    CROSSBAND_LIST[tmpcross]))
        basic.append(rs)

        # Battery save
        tmpbatsave = _mem.battery_save
        if tmpbatsave >= len(BATSAVE_LIST):
            tmpbatsave = BATSAVE_LIST.index("1:4")
        rs = RadioSetting(
                "battery_save",
                "Battery Save",
                RadioSettingValueList(
                    BATSAVE_LIST,
                    BATSAVE_LIST[tmpbatsave]))
        basic.append(rs)

        # Dual watch
        tmpdual = _mem.dual_watch
        if tmpdual >= len(DUALWATCH_LIST):
            tmpdual = 0
        rs = RadioSetting("dualwatch", "Dual Watch", RadioSettingValueList(
            DUALWATCH_LIST, DUALWATCH_LIST[tmpdual]))
        basic.append(rs)

        # Backlight auto mode
        tmpback = _mem.backlight_auto_mode
        if tmpback >= len(BACKLIGHT_LIST):
            tmpback = 0
        rs = RadioSetting("backlight_auto_mode",
                          "Backlight auto mode",
                          RadioSettingValueList(
                              BACKLIGHT_LIST,
                              BACKLIGHT_LIST[tmpback]))
        basic.append(rs)

        # Tail tone elimination
        rs = RadioSetting(
                "tail_note_elimination",
                "Tail tone elimination",
                RadioSettingValueBoolean(
                    bool(_mem.tail_note_elimination > 0)))
        basic.append(rs)

        # VFO open
        rs = RadioSetting("vfo_open", "VFO open",
                          RadioSettingValueBoolean(bool(_mem.vfo_open > 0)))
        basic.append(rs)

        # Beep control
        rs = RadioSetting(
                "beep_control",
                "Beep control",
                RadioSettingValueBoolean(bool(_mem.beep_control > 0)))
        basic.append(rs)

        # Scan resume mode
        tmpscanres = _mem.scan_resume_mode
        if tmpscanres >= len(SCANRESUME_LIST):
            tmpscanres = 0
        rs = RadioSetting(
                "scan_resume_mode",
                "Scan resume mode",
                RadioSettingValueList(
                    SCANRESUME_LIST,
                    SCANRESUME_LIST[tmpscanres]))
        basic.append(rs)

        # Keypad locked
        rs = RadioSetting(
                "key_lock",
                "Keypad lock",
                RadioSettingValueBoolean(bool(_mem.key_lock > 0)))
        basic.append(rs)

        # Auto keypad lock
        rs = RadioSetting(
                "auto_keypad_lock",
                "Auto keypad lock",
                RadioSettingValueBoolean(bool(_mem.auto_keypad_lock > 0)))
        basic.append(rs)

        # Power on display mode
        tmpdispmode = _mem.power_on_dispmode
        if tmpdispmode >= len(WELCOME_LIST):
            tmpdispmode = 0
        rs = RadioSetting(
                "welcome_mode",
                "Power on display mode",
                RadioSettingValueList(
                    WELCOME_LIST,
                    WELCOME_LIST[tmpdispmode]))
        basic.append(rs)

        # Keypad Tone
        tmpkeypadtone = _mem.keypad_tone
        if tmpkeypadtone >= len(KEYPADTONE_LIST):
            tmpkeypadtone = 0
        rs = RadioSetting("keypad_tone", "Keypad tone", RadioSettingValueList(
            KEYPADTONE_LIST, KEYPADTONE_LIST[tmpkeypadtone]))
        basic.append(rs)

        # Language
        tmplanguage = _mem.language
        if tmplanguage >= len(LANGUAGE_LIST):
            tmplanguage = 0
        rs = RadioSetting("language", "Language", RadioSettingValueList(
            LANGUAGE_LIST, LANGUAGE_LIST[tmplanguage]))
        basic.append(rs)

        # Alarm mode
        tmpalarmmode = _mem.alarm_mode
        if tmpalarmmode >= len(ALARMMODE_LIST):
            tmpalarmmode = 0
        rs = RadioSetting("alarm_mode", "Alarm mode", RadioSettingValueList(
            ALARMMODE_LIST, ALARMMODE_LIST[tmpalarmmode]))
        basic.append(rs)

        # Reminding of end of talk
        tmpalarmmode = _mem.reminding_of_end_talk
        if tmpalarmmode >= len(REMENDOFTALK_LIST):
            tmpalarmmode = 0
        rs = RadioSetting(
                "reminding_of_end_talk",
                "Reminding of end of talk",
                RadioSettingValueList(
                    REMENDOFTALK_LIST,
                    REMENDOFTALK_LIST[tmpalarmmode]))
        basic.append(rs)

        # Repeater tail tone elimination
        tmprte = _mem.repeater_tail_elimination
        if tmprte >= len(RTE_LIST):
            tmprte = 0
        rs = RadioSetting(
                "repeater_tail_elimination",
                "Repeater tail tone elimination",
                RadioSettingValueList(RTE_LIST, RTE_LIST[tmprte]))
        basic.append(rs)

        # Logo string 1
        logo1 = str(_mem.logo_line1).strip("\x20\x00\xff") + "\x00"
        logo1 = _getstring(logo1.encode('ascii', errors='ignore'), 0, 12)
        rs = RadioSetting("logo1", _("Logo string 1 (12 characters)"),
                          RadioSettingValueString(0, 12, logo1))
        basic.append(rs)

        # Logo string 2
        logo2 = str(_mem.logo_line2).strip("\x20\x00\xff") + "\x00"
        logo2 = _getstring(logo2.encode('ascii', errors='ignore'), 0, 12)
        rs = RadioSetting("logo2", _("Logo string 2 (12 characters)"),
                          RadioSettingValueString(0, 12, logo2))
        basic.append(rs)

        # FM radio
        for i in range(1, 21):
            freqname = "FM_"+str(i)
            fmfreq = _mem.fmfreq[i-1]/10.0
            if fmfreq < FMMIN or fmfreq > FMMAX:
                rs = RadioSetting(freqname, freqname,
                                  RadioSettingValueString(0, 5, ""))
            else:
                rs = RadioSetting(freqname, freqname,
                                  RadioSettingValueString(0, 5, str(fmfreq)))

            fmradio.append(rs)

        # unlock settings

        # F-LOCK
        tmpflock = _mem.lock.flock
        if tmpflock >= len(FLOCK_LIST):
            tmpflock = 0
        rs = RadioSetting(
            "flock", "F-LOCK",
            RadioSettingValueList(FLOCK_LIST, FLOCK_LIST[tmpflock]))
        unlock.append(rs)

        # 350TX
        rs = RadioSetting("tx350", "350TX - unlock 350-400 MHz TX",
                          RadioSettingValueBoolean(
                              bool(_mem.lock.tx350 > 0)))
        unlock.append(rs)

        # Killed
        rs = RadioSetting("Killed", "KILLED Device was disabled (via DTMF)",
                          RadioSettingValueBoolean(
                              bool(_mem.lock.killed > 0)))
        unlock.append(rs)

        # 200TX
        rs = RadioSetting("tx200", "200TX - unlock 174-350 MHz TX",
                          RadioSettingValueBoolean(
                              bool(_mem.lock.tx200 > 0)))
        unlock.append(rs)

        # 500TX
        rs = RadioSetting("tx500", "500TX - unlock 500-600 MHz TX",
                          RadioSettingValueBoolean(
                              bool(_mem.lock.tx500 > 0)))
        unlock.append(rs)

        # 350EN
        rs = RadioSetting("en350", "350EN - unlock 350-400 MHz RX",
                          RadioSettingValueBoolean(
                              bool(_mem.lock.en350 > 0)))
        unlock.append(rs)

        # SCREEN
        rs = RadioSetting("scrambler", "SCREN - scrambler enable",
                          RadioSettingValueBoolean(
                              bool(_mem.lock.enscramble > 0)))
        unlock.append(rs)

        # readonly info
        # Firmware
        firmware = self.metadata.get('uvk5_firmware', 'UNKNOWN')

        val = RadioSettingValueString(0, 128, firmware)
        val.set_mutable(False)
        rs = RadioSetting("fw_ver", "Firmware Version", val)
        roinfo.append(rs)

        # No limits version for hacked firmware
        val = RadioSettingValueBoolean(self._expanded_limits)
        rs = RadioSetting("nolimits", "Limits disabled for modified firmware",
                          val)
        rs.set_warning(_(
            'This should only be enabled if you are using modified firmware '
            'that supports wider frequency coverage. Enabling this will cause '
            'CHIRP not to enforce OEM restrictions and may lead to undefined '
            'or unregulated behavior. Use at your own risk!'),
            safe_value=False)
        roinfo.append(rs)

        return top

    def _set_mem_mode(self, _mem, mode):
        if mode == "NFM":
            _mem.bandwidth = 1
            _mem.enable_am = 0
        elif mode == "FM":
            _mem.bandwidth = 0
            _mem.enable_am = 0
        elif mode == "NAM":
            _mem.bandwidth = 1
            _mem.enable_am = 1
        elif mode == "AM":
            _mem.bandwidth = 0
            _mem.enable_am = 1

    # Store details about a high-level memory to the memory map
    # This is called when a user edits a memory in the UI
    def set_memory(self, mem):
        number = mem.number-1

        # Get a low-level memory object mapped to the image
        _mem = self._memobj.channel[number]
        _mem4 = self._memobj
        # empty memory
        if mem.empty:
            _mem.set_raw("\xFF" * 16)
            if number < self._channels:
                _mem2 = self._memobj.channelname[number]
                _mem2.set_raw("\xFF" * 16)
                _mem4.channel_attributes[number].is_scanlist1 = 0
                _mem4.channel_attributes[number].is_scanlist2 = 0
                # Compander in other models, not supported here
                _mem4.channel_attributes[number].compander = 0
                _mem4.channel_attributes[number].is_free = 1
                _mem4.channel_attributes[number].band = 0x7
            return mem

        # clean the channel memory, restore some bits if it was used before
        if _mem.get_raw(asbytes=False)[0] == "\xff":
            # this was an empty memory
            _mem.set_raw("\x00" * 16)
        else:
            # this memory wasn't empty, save some bits that we don't know the
            # meaning of, or that we don't support yet
            prev_0a = _mem.get_raw()[0x0a] & SAVE_MASK_0A
            prev_0b = _mem.get_raw()[0x0b] & SAVE_MASK_0B
            prev_0c = _mem.get_raw()[0x0c] & SAVE_MASK_0C
            prev_0d = _mem.get_raw()[0x0d] & SAVE_MASK_0D
            prev_0e = _mem.get_raw()[0x0e] & SAVE_MASK_0E
            prev_0f = _mem.get_raw()[0x0f] & SAVE_MASK_0F
            _mem.set_raw("\x00" * 10 +
                         chr(prev_0a) + chr(prev_0b) + chr(prev_0c) +
                         chr(prev_0d) + chr(prev_0e) + chr(prev_0f))

        if number < self._channels:
            _mem4.channel_attributes[number].is_scanlist1 = 0
            _mem4.channel_attributes[number].is_scanlist2 = 0
            _mem4.channel_attributes[number].compander = 0
            _mem4.channel_attributes[number].is_free = 1
            _mem4.channel_attributes[number].band = 0x7

        # find band
        band = _find_band(self, mem.freq)

        self._set_mem_mode(_mem, mem.mode)

        # frequency/offset
        _mem.freq = mem.freq/10
        _mem.offset = mem.offset/10

        if mem.duplex == "":
            _mem.offset = 0
            _mem.shift = 0
        elif mem.duplex == '-':
            _mem.shift = FLAGS1_OFFSET_MINUS
        elif mem.duplex == '+':
            _mem.shift = FLAGS1_OFFSET_PLUS
        elif mem.duplex == 'off':
            # we fake tx disable by setting the tx freq to 0 MHz
            _mem.shift = FLAGS1_OFFSET_MINUS
            _mem.offset = _mem.freq

        # set band
        if number < self._channels:
            _mem4.channel_attributes[number].is_free = 0
            _mem4.channel_attributes[number].band = band

        # channels >self._channels are the 14 VFO chanells and don't have names
        if number < self._channels:
            _mem2 = self._memobj.channelname[number]
            tag = mem.name.ljust(10) + "\x00"*6
            _mem2.name = tag  # Store the alpha tag

        # tone data
        self._set_tone(mem, _mem)

        # step
        _mem.step = self._steps.index(mem.tuning_step)

        # tx power
        if str(mem.power) == str(UVK5_POWER_LEVELS[2]):
            _mem.txpower = POWER_HIGH
        elif str(mem.power) == str(UVK5_POWER_LEVELS[1]):
            _mem.txpower = POWER_MEDIUM
        else:
            _mem.txpower = POWER_LOW

        for setting in mem.extra:
            sname = setting.get_name()
            svalue = setting.value.get_value()

            if sname == "bclo":
                _mem.bclo = svalue and 1 or 0

            if sname == "pttid":
                _mem.dtmf_pttid = self._pttid_list.index(svalue)

            if sname == "frev":
                _mem.freq_reverse = svalue and 1 or 0

            if sname == "dtmfdecode":
                _mem.dtmf_decode = svalue and 1 or 0

            if sname == "scrambler":
                _mem.scrambler = (
                    _mem.scrambler & 0xf0) | SCRAMBLER_LIST.index(svalue)

            if number < self._channels and sname == "scanlists":
                if svalue == "1":
                    _mem4.channel_attributes[number].is_scanlist1 = 1
                    _mem4.channel_attributes[number].is_scanlist2 = 0
                elif svalue == "2":
                    _mem4.channel_attributes[number].is_scanlist1 = 0
                    _mem4.channel_attributes[number].is_scanlist2 = 1
                elif svalue == "1+2":
                    _mem4.channel_attributes[number].is_scanlist1 = 1
                    _mem4.channel_attributes[number].is_scanlist2 = 1
                else:
                    _mem4.channel_attributes[number].is_scanlist1 = 0
                    _mem4.channel_attributes[number].is_scanlist2 = 0

        return mem


@directory.register
class UVK5Radio(UVK5RadioBase):
    @classmethod
    def k5_approve_firmware(cls, firmware):
        approved_prefixes = ('k5_2.01.', 'app_2.01.', '2.01.',
                             '1o11')
        return any(firmware.startswith(x) for x in approved_prefixes)

####################################################################
#    /'''' /''. '''/  /   /  /| /'/ /'''' /''\
#   /---  /  _   /   /   /  / |/ / /---  /.../
#  /---- /---' /--- '---'  /    / /---- /  \
####################################################################

def min_max_def(value, min_val, max_val, default):
    """returns value if in bounds or default otherwise"""
    if min_val is not None and value < min_val:
        return default
    if max_val is not None and value > max_val:
        return default
    return value


def list_def(value, lst, default):
    """return value if is in the list, default otherwise"""
    if isinstance(default, str):
        default = lst.index(default)
    if value < 0 or value >= len(lst):
        return default
    return value


@directory.register
@directory.detected_by(UVK5Radio)
class UVK5RadioEgzumerMod(UVK5RadioBase):
    """Quansheng UV-K5 (egzumer/LZ3ATZ)"""
    VENDOR = "Quansheng"
    MODEL = "UV-K5"
    VARIANT = "egzumerMod"
    BAUD_RATE = 38400
    NEEDS_COMPAT_SERIAL = False
    FIRMWARE_VERSION = ""
    _cal_start = 0x1E00  # calibration memory start address
    _cal_end= 0x2000  # calibration memory end
    _cal_len = _cal_end - _cal_start  # calibration memory length
    _mem_size = 0x2000 # eeprom total size
    _prog_size = 0x1E00 # eeprom size without calibration
    _channels = 200  # number of MR channels
    _channels_mask = 0xff  # max channel number
    _pttid_list = ["Off", "Up code", "Down code", "Up+Down code",
                   "Apollo Quindar"]
    _steps = [2.5, 5, 6.25, 10, 12.5, 25, 8.33, 0.01, 0.05, 0.1, 0.25, 0.5, 1,
              1.25, 9, 15, 20, 30, 50, 100, 125, 200, 250, 500]

    _upload_calibration = False

    @classmethod
    def k5_approve_firmware(cls, firmware):
        return firmware.startswith('EGZUMR ')

    def _get_bands(self):
        is_wide = self._memobj.BUILD_OPTIONS.ENABLE_WIDE_RX \
            if self._memobj is not None else True
        bands = BANDS_WIDE if is_wide else BANDS_STANDARD
        return bands

    def _find_band(self, hz):
        mhz = hz/1000000.0
        bands = self._get_bands()
        for bnd, rng in bands.items():
            if rng[0] <= mhz <= rng[1]:
                return bnd
        return False

    def _get_vfo_channel_names(self):
        """generates VFO_CHANNEL_NAMES"""
        bands = self._get_bands()
        names = []
        for bnd, rng in bands.items():
            name = f"F{bnd + 1}({round(rng[0])}M-{round(rng[1])}M)"
            names.append(name + "A")
            names.append(name + "B")
        return names

    def _get_specials(self):
        """generates SPECIALS"""
        specials = {}
        for idx, name in enumerate(self._get_vfo_channel_names()):
            specials[name] = self._channels + idx
        return specials

    # Return information about this radio's features, including
    # how many memories it has, what bands it supports, etc
    def get_features(self):
        rf = super().get_features()
        rf.valid_special_chans = self._get_vfo_channel_names()
        rf.valid_modes = ["FM", "NFM", "AM", "NAM", "USB"]

        rf.memory_bounds = (1, self._channels)

        rf.valid_bands = []
        bands = self._get_bands()
        for _, rng in bands.items():
            rf.valid_bands.append(
                    (int(rng[0]*1000000), int(rng[1]*1000000)))
        return rf

    # Convert the raw byte array into a memory object structure
    def process_mmap(self):
        self._check_firmware_at_load()
        self._memobj = bitwise.parse(MEM_FORMAT, self._mmap)

    def _get_mem_mode(self, _mem):
        temp_modes = self.get_features().valid_modes
        temp_modul = _mem.modulation * 2 + _mem.bandwidth
        if temp_modul < len(temp_modes):
            return temp_modes[temp_modul]
        elif temp_modul == 5:  # USB with narrow setting
            return temp_modes[4]
        elif temp_modul >= len(temp_modes):
            LOG.error('Mode %i unsupported', temp_modul)
            return "FM"

    def get_memory(self, number):
        mem = super().get_memory(number)
        try:
            number = self._get_specials()[number]
        except KeyError:
            number -= 1

        if number < self._channels:
            comp = list_def(self._memobj.channel_attributes[number].compander,
                            COMPANDER_LIST, 0)
        else:
            comp = 0
        val = RadioSettingValueList(COMPANDER_LIST, None, comp)
        rs = RadioSetting("compander", "Compander (Compnd)", val)
        mem.extra.append(rs)
        return mem

    def _set_mem_mode(self, _mem, mode):
        tmp_mode = self.get_features().valid_modes.index(mode)
        _mem.modulation = tmp_mode / 2
        _mem.bandwidth = tmp_mode % 2
        if mode == "USB":
            _mem.bandwidth = 1  # narrow

    def set_memory(self, mem):
        super().set_memory(mem)
        try:
            number = self._get_specials()[mem.number]
        except KeyError:
            number = mem.number - 1

        if number < self._channels and 'compander' in mem.extra:
            self._memobj.channel_attributes[number].compander = (
                COMPANDER_LIST.index(str(mem.extra['compander'].value)))

    def set_settings(self, settings):
        _mem = self._memobj
        for element in settings:
            if not isinstance(element, RadioSetting):
                self.set_settings(element)
                continue

            elname = element.get_name()

            # basic settings

            # VFO_A e80 ScreenChannel_A
            if elname == "VFO_A_chn":
                _mem.ScreenChannel_A = element.value
                if _mem.ScreenChannel_A < self._channels:
                    _mem.MrChannel_A = _mem.ScreenChannel_A
                elif _mem.ScreenChannel_A < (self._channels + 7):
                    _mem.FreqChannel_A = _mem.ScreenChannel_A
                else:
                    _mem.NoaaChannel_A = _mem.ScreenChannel_A

            # VFO_B e83
            elif elname == "VFO_B_chn":
                _mem.ScreenChannel_B = element.value
                if _mem.ScreenChannel_B < self._channels:
                    _mem.MrChannel_B = _mem.ScreenChannel_B
                elif _mem.ScreenChannel_B < (self._channels + 7):
                    _mem.FreqChannel_B = _mem.ScreenChannel_B
                else:
                    _mem.NoaaChannel_B = _mem.ScreenChannel_B

            # TX_VFO  channel selected A,B
            elif elname == "TX_VFO":
                _mem.TX_VFO = element.value

            # call channel
            elif elname == "call_channel":
                _mem.call_channel = element.value

            # squelch
            elif elname == "squelch":
                _mem.squelch = element.value

            # TOT
            elif elname == "tot":
                _mem.max_talk_time = element.value

            # NOAA autoscan
            elif elname == "noaa_autoscan":
                _mem.noaa_autoscan = element.value

            # VOX
            elif elname == "vox":
                voxvalue = element.value
                _mem.vox_switch = int(voxvalue) > 0
                _mem.vox_level = (voxvalue - 1) if _mem.vox_switch else 0

            # mic gain
            elif elname == "mic_gain":
                _mem.mic_gain = element.value

            # Channel display mode
            elif elname == "channel_display_mode":
                _mem.channel_display_mode = element.value

            # RX Mode
            elif elname == "rx_mode":
                tmptxmode = int(element.value)
                tmpmainvfo = _mem.TX_VFO + 1
                _mem.crossband = tmpmainvfo * bool(tmptxmode & 0b10)
                _mem.dual_watch = tmpmainvfo * bool(tmptxmode & 0b01)

            # Battery Save
            elif elname == "battery_save":
                _mem.battery_save = element.value

            # Backlight auto mode
            elif elname == "backlight_time":
                _mem.backlight_time = element.value

            # Backlight min
            elif elname == "backlight_min":
                _mem.backlight_min = element.value

            # Backlight max
            elif elname == "backlight_max":
                _mem.backlight_max = element.value

            # Backlight TX_RX
            elif elname == "backlight_on_TX_RX":
                _mem.backlight_on_TX_RX = element.value
            # AM_fix
            elif elname == "AM_fix":
                _mem.AM_fix = element.value

            # mic_bar
            elif elname == "mem.mic_bar":
                _mem.mic_bar = element.value

            # Batterie txt
            elif elname == "_mem.battery_text":
                _mem.battery_text = element.value

            # Tail tone elimination
            elif elname == "ste":
                _mem.ste = element.value

            # VFO Open
            elif elname == "freq_mode_allowed":
                _mem.freq_mode_allowed = element.value

            # Beep control
            elif elname == "button_beep":
                _mem.button_beep = element.value

            # Scan resume mode
            elif elname == "scan_resume_mode":
                _mem.scan_resume_mode = element.value

            # Keypad lock
            elif elname == "key_lock":
                _mem.key_lock = element.value

            # Auto keypad lock
            elif elname == "auto_keypad_lock":
                _mem.auto_keypad_lock = element.value

            # Power on display mode
            elif elname == "welcome_mode":
                _mem.power_on_dispmode = element.value

            # Keypad Tone
            elif elname == "voice":
                _mem.voice = element.value

            elif elname == "s0_level":
                _mem.s0_level = element.value * -1

            elif elname == "s9_level":
                _mem.s9_level = element.value * -1

            elif elname == "password":
                if element.value.get_value() is None or element.value == "":
                    _mem.password = 0xFFFFFFFF
                else:
                    _mem.password = element.value

            # Alarm mode
            elif elname == "alarm_mode":
                _mem.alarm_mode = element.value

            # Reminding of end of talk
            elif elname == "roger_beep":
                _mem.roger_beep = element.value

            # Repeater tail tone elimination
            elif elname == "rp_ste":
                _mem.rp_ste = element.value

            # Logo string 1
            elif elname == "logo1":
                bts = str(element.value).rstrip("\x20\xff\x00")+"\x00" * 12
                _mem.logo_line1 = bts[0:12] + "\x00\xff\xff\xff"

            # Logo string 2
            elif elname == "logo2":
                bts = str(element.value).rstrip("\x20\xff\x00")+"\x00" * 12
                _mem.logo_line2 = bts[0:12] + "\x00\xff\xff\xff"

            # unlock settings

            # FLOCK
            elif elname == "int_flock":
                _mem.int_flock = element.value

            # 350TX
            elif elname == "int_350tx":
                _mem.int_350tx = element.value

            # KILLED
            elif elname == "int_KILLED":
                _mem.int_KILLED = element.value

            # 200TX
            elif elname == "int_200tx":
                _mem.int_200tx = element.value

            # 500TX
            elif elname == "int_500tx":
                _mem.int_500tx = element.value

            # 350EN
            elif elname == "int_350en":
                _mem.int_350en = element.value

            # SCREN
            elif elname == "int_scren":
                _mem.int_scren = element.value

            # battery type
            elif elname == "Battery_type":
                _mem.Battery_type = element.value
            # fm radio
            for i in range(1, 21):
                freqname = "FM_%i" % i
                if elname == freqname:
                    val = str(element.value).strip()
                    try:
                        val2 = int(float(val) * 10)
                    except Exception:
                        val2 = 0xffff

                    if val2 < FMMIN * 10 or val2 > FMMAX * 10:
                        val2 = 0xffff
#                        raise errors.InvalidValueError(
#                                "FM radio frequency should be a value "
#                                "in the range %.1f - %.1f" % (FMMIN , FMMAX))
                    _mem.fmfreq[i-1] = val2

            # dtmf settings
            if elname == "dtmf_side_tone":
                _mem.dtmf.side_tone = element.value

            elif elname == "dtmf_separate_code":
                _mem.dtmf.separate_code = element.value

            elif elname == "dtmf_group_call_code":
                _mem.dtmf.group_call_code = element.value

            elif elname == "dtmf_decode_response":
                _mem.dtmf.decode_response = element.value

            elif elname == "dtmf_auto_reset_time":
                _mem.dtmf.auto_reset_time = element.value

            elif elname == "dtmf_preload_time":
                _mem.dtmf.preload_time = element.value // 10

            elif elname == "dtmf_first_code_persist_time":
                _mem.dtmf.first_code_persist_time = element.value // 10

            elif elname == "dtmf_hash_persist_time":
                _mem.dtmf.hash_persist_time = element.value // 10

            elif elname == "dtmf_code_persist_time":
                _mem.dtmf.code_persist_time = element.value // 10

            elif elname == "dtmf_code_interval_time":
                _mem.dtmf.code_interval_time = element.value // 10

            elif elname == "dtmf_permit_remote_kill":
                _mem.dtmf.permit_remote_kill = element.value

            elif elname == "dtmf_dtmf_local_code":
                k = str(element.value).rstrip("\x20\xff\x00") + "\x00" * 3
                _mem.dtmf.local_code = k[0:3]

            elif elname == "dtmf_dtmf_up_code":
                k = str(element.value).strip("\x20\xff\x00") + "\x00" * 16
                _mem.dtmf.up_code = k[0:16]

            elif elname == "dtmf_dtmf_down_code":
                k = str(element.value).rstrip("\x20\xff\x00") + "\x00" * 16
                _mem.dtmf.down_code = k[0:16]

            elif elname == "dtmf_kill_code":
                k = str(element.value).strip("\x20\xff\x00") + "\x00" * 5
                _mem.dtmf.kill_code = k[0:5]

            elif elname == "dtmf_revive_code":
                k = str(element.value).strip("\x20\xff\x00") + "\x00" * 5
                _mem.dtmf.revive_code = k[0:5]

            elif elname == "live_DTMF_decoder":
                _mem.live_DTMF_decoder = element.value

            # dtmf contacts
            for i in range(1, 17):
                varname = "DTMF_%i" % i
                if elname == varname:
                    k = str(element.value).rstrip("\x20\xff\x00") + "\x00" * 8
                    _mem.dtmfcontact[i-1].name = k[0:8]

                varnumname = "DTMFNUM_%i" % i
                if elname == varnumname:
                    k = str(element.value).rstrip("\x20\xff\x00") + "\xff" * 3
                    _mem.dtmfcontact[i-1].number = k[0:3]

            # scanlist stuff
            if elname == "slDef":
                _mem.slDef = element.value

            elif elname == "sl1PriorEnab":
                _mem.sl1PriorEnab = element.value

            elif elname == "sl2PriorEnab":
                _mem.sl2PriorEnab = element.value

            elif elname in ["sl1PriorCh1", "sl1PriorCh2", "sl2PriorCh1",
                            "sl2PriorCh2"]:
                val = int(element.value)
                if val > self._channels or val < 1:
                    val = self._channels_mask
                else:
                    val -= 1

                _mem[elname] = val

            if elname == "key1_shortpress_action":
                _mem.key1_shortpress_action = element.value

            elif elname == "key1_longpress_action":
                _mem.key1_longpress_action = element.value

            elif elname == "key2_shortpress_action":
                _mem.key2_shortpress_action = element.value

            elif elname == "key2_longpress_action":
                _mem.key2_longpress_action = element.value

            elif elname == "keyM_longpress_action":
                _mem.keyM_longpress_action = element.value

            elif element.changed() and elname.startswith("cal."):
                _mem.get_path(elname).set_value(element.value)

    def get_settings(self):
        _mem = self._memobj
        basic = RadioSettingGroup("basic", "Basic Settings")
        advanced = RadioSettingGroup("advanced", "Advanced Settings")
        keya = RadioSettingGroup("keya", "Programmable Keys")
        dtmf = RadioSettingGroup("dtmf", "DTMF Settings")
        dtmfc = RadioSettingGroup("dtmfc", "DTMF Contacts")
        scanl = RadioSettingGroup("scn", "Scan Lists")
        unlock = RadioSettingGroup("unlock", "Unlock Settings")
        fmradio = RadioSettingGroup("fmradio", "FM Radio")
        calibration = RadioSettingGroup("calibration", "Calibration")

        roinfo = RadioSettingGroup("roinfo", "Driver Information")
        top = RadioSettings()
        top.append(basic)
        top.append(advanced)
        top.append(keya)
        top.append(dtmf)
        if _mem.BUILD_OPTIONS.ENABLE_DTMF_CALLING:
            top.append(dtmfc)
        top.append(scanl)
        top.append(unlock)
        if _mem.BUILD_OPTIONS.ENABLE_FMRADIO:
            top.append(fmradio)
        top.append(roinfo)
        top.append(calibration)

        # helper function
        def append_label(radio_setting, label, descr=""):
            if not hasattr(append_label, 'idx'):
                append_label.idx = 0

            val = RadioSettingValueString(len(descr), len(descr), descr)
            val.set_mutable(False)
            rs = RadioSetting("label%s" % append_label.idx, label, val)
            append_label.idx += 1
            radio_setting.append(rs)

        # Programmable keys
        def get_action(action_num):
            """"get actual key action"""
            has_alarm = self._memobj.BUILD_OPTIONS.ENABLE_ALARM
            has1750 = self._memobj.BUILD_OPTIONS.ENABLE_TX1750
            has_flashlight = self._memobj.BUILD_OPTIONS.ENABLE_FLASHLIGHT
            lst = KEYACTIONS_LIST.copy()
            if not has_alarm:
                lst.remove("Alarm")
            if not has1750:
                lst.remove("1750Hz tone")
            if not has_flashlight:
                lst.remove("Flashlight")

            action_num = int(action_num)
            if action_num >= len(KEYACTIONS_LIST) or \
               KEYACTIONS_LIST[action_num] not in lst:
                action_num = 0
            return lst, KEYACTIONS_LIST[action_num]

        val = RadioSettingValueList(*get_action(_mem.key1_shortpress_action))
        rs = RadioSetting("key1_shortpress_action",
                          "Side key 1 short press (F1Shrt)", val)
        keya.append(rs)

        val = RadioSettingValueList(*get_action(_mem.key1_longpress_action))
        rs = RadioSetting("key1_longpress_action",
                          "Side key 1 long press (F1Long)", val)
        keya.append(rs)

        val = RadioSettingValueList(*get_action(_mem.key2_shortpress_action))
        rs = RadioSetting("key2_shortpress_action",
                          "Side key 2 short press (F2Shrt)", val)
        keya.append(rs)

        val = RadioSettingValueList(*get_action(_mem.key2_longpress_action))
        rs = RadioSetting("key2_longpress_action",
                          "Side key 2 long press (F2Long)", val)
        keya.append(rs)

        val = RadioSettingValueList(*get_action(_mem.keyM_longpress_action))
        rs = RadioSetting("keyM_longpress_action",
                          "Menu key long press (M Long)", val)
        keya.append(rs)

        # ----------------- DTMF settings

        tmpval = str(_mem.dtmf.separate_code)
        if tmpval not in DTMF_CODE_CHARS:
            tmpval = '*'
        val = RadioSettingValueString(1, 1, tmpval)
        val.set_charset(DTMF_CODE_CHARS)
        sep_code_setting = RadioSetting("dtmf_separate_code",
                                        "Separate Code", val)

        tmpval = str(_mem.dtmf.group_call_code)
        if tmpval not in DTMF_CODE_CHARS:
            tmpval = '#'
        val = RadioSettingValueString(1, 1, tmpval)
        val.set_charset(DTMF_CODE_CHARS)
        group_code_setting = RadioSetting("dtmf_group_call_code",
                                          "Group Call Code", val)

        tmpval = min_max_def(_mem.dtmf.first_code_persist_time * 10,
                             30, 1000, 300)
        val = RadioSettingValueInteger(30, 1000, tmpval, 10)
        first_code_per_setting = \
            RadioSetting("dtmf_first_code_persist_time",
                         "First code persist time (ms)", val)

        tmpval = min_max_def(_mem.dtmf.hash_persist_time * 10, 30, 1000, 300)
        val = RadioSettingValueInteger(30, 1000, tmpval, 10)
        spec_per_setting = RadioSetting("dtmf_hash_persist_time",
                                        "#/* persist time (ms)", val)

        tmpval = min_max_def(_mem.dtmf.code_persist_time * 10, 30, 1000, 300)
        val = RadioSettingValueInteger(30, 1000, tmpval, 10)
        code_per_setting = RadioSetting("dtmf_code_persist_time",
                                        "Code persist time (ms)", val)

        tmpval = min_max_def(_mem.dtmf.code_interval_time * 10, 30, 1000, 300)
        val = RadioSettingValueInteger(30, 1000, tmpval, 10)
        code_int_setting = RadioSetting("dtmf_code_interval_time",
                                        "Code interval time (ms)", val)

        tmpval = str(_mem.dtmf.local_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_ID:
                continue
            tmpval = "103"
            break
        val = RadioSettingValueString(3, 3, tmpval)
        val.set_charset(DTMF_CHARS_ID)
        ani_id_setting = \
            RadioSetting("dtmf_dtmf_local_code",
                         "Local code (ANI ID)", val)
        ani_id_setting.set_doc('3 chars 0-9 ABCD')

        tmpval = str(_mem.dtmf.up_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_UPDOWN or i == "":
                continue
            else:
                tmpval = "123"
                break
        val = RadioSettingValueString(1, 16, tmpval)
        val.set_charset(DTMF_CHARS_UPDOWN)
        up_code_setting = \
            RadioSetting("dtmf_dtmf_up_code",
                         "Up code", val)
        up_code_setting.set_doc('1-16 chars 0-9 ABCD*#')

        tmpval = str(_mem.dtmf.down_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_UPDOWN:
                continue
            else:
                tmpval = "456"
                break
        val = RadioSettingValueString(1, 16, tmpval)
        val.set_charset(DTMF_CHARS_UPDOWN)
        dw_code_setting = \
            RadioSetting("dtmf_dtmf_down_code",
                         "Down code", val)
        dw_code_setting.set_doc('1-16 chars 0-9 ABCD*#')

        val = RadioSettingValueBoolean(_mem.dtmf.side_tone)
        dtmf_side_tone_setting = \
            RadioSetting("dtmf_side_tone",
                         "DTMF Sidetone on speaker when sent (D ST)", val)

        tmpval = list_def(_mem.dtmf.decode_response,
                          DTMF_DECODE_RESPONSE_LIST, 0)
        val = RadioSettingValueList(DTMF_DECODE_RESPONSE_LIST, None, tmpval)
        dtmf_resp_setting = RadioSetting("dtmf_decode_response",
                                         "Decode Response (D Resp)", val)

        tmpval = min_max_def(_mem.dtmf.auto_reset_time, 5, 60, 10)
        val = RadioSettingValueInteger(5, 60, tmpval)
        d_hold_setting = RadioSetting("dtmf_auto_reset_time",
                                      "Auto reset time (s) (D Hold)", val)

        # D Prel
        tmpval = min_max_def(_mem.dtmf.preload_time * 10, 30, 990, 300)
        val = RadioSettingValueInteger(30, 990, tmpval, 10)
        d_prel_setting = RadioSetting("dtmf_preload_time",
                                      "Pre-load time (ms) (D Prel)", val)

        # D LIVE
        val = RadioSettingValueBoolean(_mem.live_DTMF_decoder)
        d_live_setting = \
            RadioSetting("live_DTMF_decoder", "Displays DTMF codes"
                         " received in the middle of the screen (D Live)", val)

        val = RadioSettingValueBoolean(_mem.dtmf.permit_remote_kill)
        perm_kill_setting = RadioSetting("dtmf_permit_remote_kill",
                                         "Permit remote kill", val)

        tmpval = str(_mem.dtmf.kill_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_KILL:
                continue
            else:
                tmpval = "77777"
                break
        if not len(tmpval) == 5:
            tmpval = "77777"
        val = RadioSettingValueString(5, 5, tmpval)
        val.set_charset(DTMF_CHARS_KILL)
        kill_code_setting = RadioSetting("dtmf_kill_code",
                                         "Kill code", val)
        kill_code_setting.set_doc('5 chars 0-9 ABCD')

        tmpval = str(_mem.dtmf.revive_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_KILL:
                continue
            else:
                tmpval = "88888"
                break
        if not len(tmpval) == 5:
            tmpval = "88888"
        val = RadioSettingValueString(5, 5, tmpval)
        val.set_charset(DTMF_CHARS_KILL)
        rev_code_setting = RadioSetting("dtmf_revive_code",
                                        "Revive code", val)
        rev_code_setting.set_doc('5 chars 0-9 ABCD')

        val = RadioSettingValueBoolean(_mem.int_KILLED)
        killed_setting = RadioSetting("int_KILLED", "DTMF kill lock", val)

        # ----------------- DTMF Contacts

        for i in range(1, 17):
            varname = "DTMF_"+str(i)
            varnumname = "DTMFNUM_"+str(i)
            vardescr = "DTMF Contact "+str(i)+" name"
            varinumdescr = "DTMF Contact "+str(i)+" number"

            cntn = str(_mem.dtmfcontact[i-1].name).strip("\x20\x00\xff")
            cntnum = str(_mem.dtmfcontact[i-1].number).strip("\x20\x00\xff")

            val = RadioSettingValueString(0, 8, cntn)
            rs = RadioSetting(varname, vardescr, val)
            dtmfc.append(rs)

            val = RadioSettingValueString(0, 3, cntnum)
            val.set_charset(DTMF_CHARS)
            rs = RadioSetting(varnumname, varinumdescr, val)
            rs.set_doc("DTMF Contacts are 3 codes (valid: 0-9 * # ABCD), "
                       "or an empty string")
            dtmfc.append(rs)

        # ----------------- Scan Lists

        tmpscanl = list_def(_mem.slDef, SCANLIST_SELECT_LIST, 0)
        val = RadioSettingValueList(SCANLIST_SELECT_LIST, None, tmpscanl)
        rs = RadioSetting("slDef", "Default scanlist (SList)", val)
        scanl.append(rs)

        val = RadioSettingValueBoolean(_mem.sl1PriorEnab)
        rs = RadioSetting("sl1PriorEnab", "List 1 priority channel scan", val)
        scanl.append(rs)

        ch_list = ["None"]
        for ch in range(1, self._channels + 1):
            ch_list.append("Channel M%i" % ch)

        tmpch = list_def(_mem.sl1PriorCh1 + 1, ch_list, 0)
        val = RadioSettingValueList(ch_list, None, tmpch)
        rs = RadioSetting("sl1PriorCh1", "List 1 priority channel 1", val)
        scanl.append(rs)

        tmpch = list_def(_mem.sl1PriorCh2 + 1, ch_list, 0)
        val = RadioSettingValueList(ch_list, None, tmpch)
        rs = RadioSetting("sl1PriorCh2", "List 1 priority channel 2", val)
        scanl.append(rs)

        val = RadioSettingValueBoolean(_mem.sl2PriorEnab)
        rs = RadioSetting("sl2PriorEnab", "List 2 priority channel scan", val)
        scanl.append(rs)

        tmpch = list_def(_mem.sl2PriorCh1 + 1, ch_list, 0)
        val = RadioSettingValueList(ch_list, None, tmpch)
        rs = RadioSetting("sl2PriorCh1", "List 2 priority channel 1", val)
        scanl.append(rs)

        tmpch = list_def(_mem.sl2PriorCh2 + 1, ch_list, 0)
        val = RadioSettingValueList(ch_list, None, tmpch)
        rs = RadioSetting("sl2PriorCh2", "List 2 priority channel 2", val)
        scanl.append(rs)

        # ----------------- Basic settings

        ch_list = []
        for ch in range(1, self._channels + 1):
            ch_list.append("Channel M%i" % ch)
        for bnd in range(1, 8):
            ch_list.append("Band F%i" % bnd)
        if _mem.BUILD_OPTIONS.ENABLE_NOAA:
            for bnd in range(1, 11):
                ch_list.append("NOAA N%i" % bnd)

        tmpfreq0 = list_def(_mem.ScreenChannel_A, ch_list, 0)
        val = RadioSettingValueList(ch_list, None, tmpfreq0)
        freq0_setting = RadioSetting("VFO_A_chn",
                                     "VFO A current channel/band", val)

        tmpfreq1 = list_def(_mem.ScreenChannel_B, ch_list, 0)
        val = RadioSettingValueList(ch_list, None, tmpfreq1)
        freq1_setting = RadioSetting("VFO_B_chn",
                                     "VFO B current channel/band", val)

        tmptxvfo = list_def(_mem.TX_VFO, TX_VFO_LIST, 0)
        val = RadioSettingValueList(TX_VFO_LIST, None, tmptxvfo)
        tx_vfo_setting = RadioSetting("TX_VFO", "Main VFO", val)

        tmpsq = min_max_def(_mem.squelch, 0, 9, 1)
        val = RadioSettingValueInteger(0, 9, tmpsq)
        squelch_setting = RadioSetting("squelch", "Squelch (Sql)", val)

        ch_list = []
        for ch in range(1, 201):
            ch_list.append("Channel M%i" % ch)

        tmpc = list_def(_mem.call_channel, ch_list, 0)
        val = RadioSettingValueList(ch_list, None, tmpc)
        call_channel_setting = RadioSetting("call_channel",
                                            "One key call channel (1 Call)",
                                            val)

        val = RadioSettingValueBoolean(_mem.key_lock)
        keypad_cock_setting = RadioSetting("key_lock", "Keypad locked", val)

        val = RadioSettingValueBoolean(_mem.auto_keypad_lock)
        auto_keypad_lock_setting = \
            RadioSetting("auto_keypad_lock",
                         "Auto keypad lock (KeyLck)", val)

        tmptot = list_def(_mem.max_talk_time,  TALK_TIME_LIST, 1)
        val = RadioSettingValueList(TALK_TIME_LIST, None, tmptot)
        tx_t_out_setting = RadioSetting("tot",
                                        "Max talk, TX Time Out (TxTOut)", val)

        tmpbatsave = list_def(_mem.battery_save, BATSAVE_LIST, 4)
        val = RadioSettingValueList(BATSAVE_LIST, None, tmpbatsave)
        bat_save_setting = RadioSetting("battery_save",
                                        "Battery save (BatSav)", val)

        val = RadioSettingValueBoolean(_mem.noaa_autoscan)
        noaa_auto_scan_setting = RadioSetting("noaa_autoscan",
                                              "NOAA Autoscan (NOAA-S)", val)

        tmpmicgain = list_def(_mem.mic_gain, MIC_GAIN_LIST, 2)
        val = RadioSettingValueList(MIC_GAIN_LIST, None, tmpmicgain)
        mic_gain_setting = RadioSetting("mic_gain", "Mic Gain (Mic)", val)

        val = RadioSettingValueBoolean(_mem.mic_bar)
        mic_bar_setting = RadioSetting("mic_bar",
                                       "Microphone Bar display (MicBar)", val)

        tmpchdispmode = list_def(_mem.channel_display_mode,
                                 CHANNELDISP_LIST, 0)
        val = RadioSettingValueList(CHANNELDISP_LIST, None, tmpchdispmode)
        ch_disp_setting = RadioSetting("channel_display_mode",
                                       "Channel display mode (ChDisp)", val)

        tmpdispmode = list_def(_mem.power_on_dispmode, WELCOME_LIST, 0)
        val = RadioSettingValueList(WELCOME_LIST, None, tmpdispmode)
        p_on_msg_setting = RadioSetting("welcome_mode",
                                        "Power ON display message (POnMsg)",
                                        val)

        logo1 = str(_mem.logo_line1).strip("\x20\x00\xff") + "\x00"
        logo1 = _getstring(logo1.encode('ascii', errors='ignore'), 0, 12)
        val = RadioSettingValueString(0, 12, logo1)
        logo1_setting = RadioSetting("logo1",
                                     "Message line 1",
                                     val)

        logo2 = str(_mem.logo_line2).strip("\x20\x00\xff") + "\x00"
        logo2 = _getstring(logo2.encode('ascii', errors='ignore'), 0, 12)
        val = RadioSettingValueString(0, 12, logo2)
        logo2_setting = RadioSetting("logo2",
                                     "Message line 2",
                                     val)

        tmpbattxt = list_def(_mem.battery_text, BAT_TXT_LIST, 2)
        val = RadioSettingValueList(BAT_TXT_LIST, None, tmpbattxt)
        bat_txt_setting = RadioSetting("battery_text",
                                       "Battery Level Display (BatTXT)", val)

        tmpback = list_def(_mem.backlight_time, BACKLIGHT_LIST, 0)
        val = RadioSettingValueList(BACKLIGHT_LIST, None, tmpback)
        back_lt_setting = RadioSetting("backlight_time",
                                       "Backlight time (BackLt)", val)

        tmpback = list_def(_mem.backlight_min, BACKLIGHT_LVL_LIST, 0)
        val = RadioSettingValueList(BACKLIGHT_LVL_LIST, None, tmpback)
        bl_min_setting = RadioSetting("backlight_min",
                                      "Backlight level min (BLMin)", val)

        tmpback = list_def(_mem.backlight_max, BACKLIGHT_LVL_LIST, 10)
        val = RadioSettingValueList(BACKLIGHT_LVL_LIST, None, tmpback)
        bl_max_setting = RadioSetting("backlight_max",
                                      "Backlight level max (BLMax)", val)

        tmpback = list_def(_mem.backlight_on_TX_RX, BACKLIGHT_TX_RX_LIST, 0)
        val = RadioSettingValueList(BACKLIGHT_TX_RX_LIST, None, tmpback)
        blt_trx_setting = RadioSetting("backlight_on_TX_RX",
                                       "Backlight on TX/RX (BltTRX)", val)

        val = RadioSettingValueBoolean(_mem.button_beep)
        beep_setting = RadioSetting("button_beep",
                                    "Key press beep sound (Beep)", val)

        tmpalarmmode = list_def(_mem.roger_beep, ROGER_LIST, 0)
        val = RadioSettingValueList(ROGER_LIST, None, tmpalarmmode)
        roger_setting = RadioSetting("roger_beep",
                                     "End of transmission beep (Roger)", val)

        val = RadioSettingValueBoolean(_mem.ste)
        ste_setting = RadioSetting("ste", "Squelch tail elimination (STE)",
                                   val)

        tmprte = list_def(_mem.rp_ste, RTE_LIST, 0)
        val = RadioSettingValueList(RTE_LIST, None, tmprte)
        rp_ste_setting = \
            RadioSetting("rp_ste",
                         "Repeater squelch tail elimination (RP STE)", val)

        val = RadioSettingValueBoolean(_mem.AM_fix)
        am_fix_setting = RadioSetting("AM_fix",
                                      "AM reception fix (AM Fix)", val)

        tmpvox = min_max_def((_mem.vox_level + 1) * _mem.vox_switch, 0, 10, 0)
        val = RadioSettingValueList(VOX_LIST, None, tmpvox)
        vox_setting = RadioSetting("vox", "Voice-operated switch (VOX)", val)

        tmprxmode = list_def((bool(_mem.crossband) << 1)
                             + bool(_mem.dual_watch),
                             RXMODE_LIST, 0)
        val = RadioSettingValueList(RXMODE_LIST, None, tmprxmode)
        rx_mode_setting = RadioSetting("rx_mode", "RX Mode (RxMode)", val)

        val = RadioSettingValueBoolean(_mem.freq_mode_allowed)
        freq_mode_allowed_setting = RadioSetting("freq_mode_allowed",
                                                 "Frequency mode allowed", val)

        tmpscanres = list_def(_mem.scan_resume_mode, SCANRESUME_LIST, 0)
        val = RadioSettingValueList(SCANRESUME_LIST, None, tmpscanres)
        scn_rev_setting = RadioSetting("scan_resume_mode",
                                       "Scan resume mode (ScnRev)", val)

        tmpvoice = list_def(_mem.voice, VOICE_LIST, 0)
        val = RadioSettingValueList(VOICE_LIST, None, tmpvoice)
        voice_setting = RadioSetting("voice", "Voice", val)

        tmpalarmmode = list_def(_mem.alarm_mode, ALARMMODE_LIST, 0)
        val = RadioSettingValueList(ALARMMODE_LIST, None, tmpalarmmode)
        alarm_setting = RadioSetting("alarm_mode", "Alarm mode", val)

        # ----------------- Extra settings

        # S-meter
        tmp_s0 = -int(_mem.s0_level)
        tmp_s9 = -int(_mem.s9_level)

        if tmp_s0 not in range(-200, -91) or tmp_s9 not in range(-160, -51) \
           or tmp_s9 < tmp_s0+9:

            tmp_s0 = -130
            tmp_s9 = -76
        val = RadioSettingValueInteger(-200, -90, tmp_s0)
        s0_level_setting = RadioSetting("s0_level",
                                        "S-meter S0 level [dBm]", val)

        val = RadioSettingValueInteger(-160, -50, tmp_s9)
        s9_level_setting = RadioSetting("s9_level",
                                        "S-meter S9 level [dBm]", val)

        # Battery Type
        tmpbtype = list_def(_mem.Battery_type, BATTYPE_LIST, 0)
        val = RadioSettingValueList(BATTYPE_LIST, BATTYPE_LIST[tmpbtype])
        bat_type_setting = RadioSetting("Battery_type",
                                        "Battery Type (BatTyp)", val)

        # Power on password
        def validate_password(value):
            value = value.strip(" ")
            if value.isdigit():
                return value.zfill(6)
            if value != "":
                raise InvalidValueError("Power on password "
                                        "can only have digits")
            return ""

        pswd_str = str(int(_mem.password)).zfill(6) \
            if _mem.password < 1000000 else ""
        val = RadioSettingValueString(0, 6, pswd_str)
        val.set_validate_callback(validate_password)
        pswd_setting = RadioSetting("password", "Power on password", val)

        # ----------------- FM radio

        for i in range(1, 21):
            fmfreq = _mem.fmfreq[i-1] / 10.0
            freq_name = str(fmfreq)
            if fmfreq < FMMIN or fmfreq > FMMAX:
                freq_name = ""
            rs = RadioSetting("FM_%i" % i, "Ch %i" % i,
                              RadioSettingValueString(0, 5, freq_name))
            fmradio.append(rs)
            rs.set_doc('Frequency in MHz')

        # ----------------- Unlock settings

        # F-LOCK
        def validate_int_flock(value):
            mem_val = self._memobj.int_flock
            if mem_val != 7 and value == FLOCK_LIST[7]:
                msg = "%r can only be enabled from radio menu" % value
                raise InvalidValueError(msg)
            return value

        tmpflock = list_def(_mem.int_flock, FLOCK_LIST, 0)
        val = RadioSettingValueList(FLOCK_LIST, None, tmpflock)
        val.set_validate_callback(validate_int_flock)
        f_lock_setting = RadioSetting("int_flock",
                                      "TX Frequency Lock (F Lock)", val)

        val = RadioSettingValueBoolean(_mem.int_200tx)
        tx200_setting = RadioSetting("int_200tx",
                                     "Unlock 174-350MHz TX (Tx 200)", val)

        val = RadioSettingValueBoolean(_mem.int_350tx)
        tx350_setting = RadioSetting("int_350tx",
                                     "Unlock 350-400MHz TX (Tx 350)", val)

        val = RadioSettingValueBoolean(_mem.int_500tx)
        tx500_setting = RadioSetting("int_500tx",
                                     "Unlock 500-600MHz TX (Tx 500)", val)

        val = RadioSettingValueBoolean(_mem.int_350en)
        en350_setting = RadioSetting("int_350en",
                                     "Unlock 350-400MHz RX (350 En)", val)

        val = RadioSettingValueBoolean(_mem.int_scren)
        en_scrambler_setting = RadioSetting("int_scren",
                                            "Scrambler enabled (ScraEn)", val)

        # ----------------- Driver Info

        firmware = self.metadata.get('uvk5_firmware', 'UNKNOWN')
        append_label(roinfo, "Firmware Version", firmware)

        # ----------------- Calibration

        val = RadioSettingValueBoolean(False)

        radio_setting = RadioSetting("_upload_calibration",
                                     "Upload calibration", val)
        radio_setting.set_warning(
            _('This option may break your radio! '
              'Each radio has a unique set of calibration data '
              'and uploading the data from the image will cause '
              'physical harm to the radio if it is from a '
              'different piece of hardware. Do not use this '
              'unless you know what you are doing and accept the '
              'risk of destroying your radio!'),
            safe_value=False)
        calibration.append(radio_setting)

        radio_setting_group = RadioSettingGroup("squelch_calibration",
                                                "Squelch")
        calibration.append(radio_setting_group)

        bands = {"sqlBand1_3": "Frequency Band 1-3",
                 "sqlBand4_7": "Frequency Band 4-7"}
        for bnd, bndn in bands.items():
            band_group_range = RadioSettingSubGroup(bnd, bndn)
            radio_setting_group.append(band_group_range)
            for sql in range(0, 10):
                band_group = RadioSettingSubGroup(
                    '%s_%i' % (bnd, sql),
                    "Squelch %i" % sql)
                band_group_range.append(band_group)

                name = 'cal.%s.openRssiThr[%i]' % (bnd, sql)
                tempval = min_max_def(_mem.get_path(name), 0, 255, 0)
                val = RadioSettingValueInteger(0, 255, tempval)
                radio_setting = RadioSetting(name, "RSSI threshold open", val)
                band_group.append(radio_setting)

                name = 'cal.%s.closeRssiThr[%i]' % (bnd, sql)
                tempval = min_max_def(_mem.get_path(name), 0, 255, 0)
                val = RadioSettingValueInteger(0, 255, tempval)
                radio_setting = RadioSetting(name, "RSSI threshold close", val)
                band_group.append(radio_setting)

                name = "cal.%s.openNoiseThr[%i]" % (bnd, sql)
                tempval = min_max_def(_mem.get_path(name), 0, 127, 0)
                val = RadioSettingValueInteger(0, 127, tempval)
                radio_setting = RadioSetting(name, "Noise threshold open", val)
                band_group.append(radio_setting)

                name = "cal.%s.closeNoiseThr[%i]" % (bnd, sql)
                tempval = min_max_def(_mem.get_path(name), 0, 127, 0)
                val = RadioSettingValueInteger(0, 127, tempval)
                radio_setting = RadioSetting(name, "Noise threshold close",
                                             val)
                band_group.append(radio_setting)

                name = "cal.%s.openGlitchThr[%i]" % (bnd, sql)
                tempval = min_max_def(_mem.get_path(name), 0, 255, 0)
                val = RadioSettingValueInteger(0, 255, tempval)
                radio_setting = RadioSetting(name, "Glitch threshold open",
                                             val)
                band_group.append(radio_setting)

                name = "cal.%s.closeGlitchThr[%i]" % (bnd, sql)
                tempval = min_max_def(_mem.get_path(name), 0, 255, 0)
                val = RadioSettingValueInteger(0, 255, tempval)
                radio_setting = RadioSetting(name, "Glitch threshold close",
                                             val)
                band_group.append(radio_setting)

#

        radio_setting_group = RadioSettingGroup("rssi_level_calibration",
                                                "RSSI levels")
        calibration.append(radio_setting_group)

        bands = {"rssiLevelsBands1_2": "1-2 ", "rssiLevelsBands3_7": "3-7 "}
        for bnd, bndn in bands.items():
            band_group = RadioSettingSubGroup(bnd, 'Frequency Band %s' % bndn)
            radio_setting_group.append(band_group)

            for lvl in [1, 2, 4, 6]:
                name = "cal.%s.level%i" % (bnd, lvl)
                value = int(_mem.get_path(name))
                tempval = min_max_def(value, 0, 65535, 0)
                val = RadioSettingValueInteger(0, 65535, tempval)
                radio_setting = RadioSetting(name, "Level %i" % lvl, val)
                band_group.append(radio_setting)

#

        radio_setting_group = RadioSettingGroup("tx_power_calibration",
                                                "TX power")
        calibration.append(radio_setting_group)

        for bnd in range(0, 7):
            band_group = RadioSettingSubGroup('txpower_band_%i' % bnd,
                                              'Band %i' % (bnd + 1))
            powers = {"low": "Low", "mid": "Medium", "hi": "High"}
            radio_setting_group.append(band_group)
            for pwr, pwrn in powers.items():
                bounds = ["lower", "center", "upper"]
                subgroup = RadioSettingSubGroup('txpower_band_%i_%s' % (
                    bnd, pwr), pwrn)
                band_group.append(subgroup)
                for bound in bounds:
                    name = f"cal.txp[{bnd}].{pwr}.{bound}"
                    tempval = min_max_def(_mem.get_path(name), 0, 255, 0)
                    val = RadioSettingValueInteger(0, 255, tempval)
                    radio_setting = RadioSetting(name, bound.capitalize(), val)
                    subgroup.append(radio_setting)

#

        radio_setting_group = RadioSettingGroup("battery_calibration",
                                                "Battery")
        calibration.append(radio_setting_group)

        for lvl in range(0, 6):
            name = "cal.batLvl[%i]" % lvl
            temp_val = min_max_def(_mem.get_path(name), 0, 4999, 4999)
            val = RadioSettingValueInteger(0, 4999, temp_val)
            label = 'Level %i%s' % (
                lvl,
                " (voltage calibration)" if lvl == 3 else "")
            radio_setting = RadioSetting(name, label, val)
            radio_setting_group.append(radio_setting)

        radio_setting_group = RadioSettingGroup("vox_calibration", "VOX")
        calibration.append(radio_setting_group)

        for lvl in range(0, 10):
            name = "cal.vox1Thr[%s]" % lvl
            val = RadioSettingValueInteger(0, 65535, _mem.get_path(name))
            radio_setting = RadioSetting(name, "Level %i On" % (lvl + 1), val)
            radio_setting_group.append(radio_setting)

            name = "cal.vox0Thr[%s]" % lvl
            val = RadioSettingValueInteger(0, 65535, _mem.get_path(name))
            radio_setting = RadioSetting(name, "Level %i Off" % (lvl + 1), val)
            radio_setting_group.append(radio_setting)

        radio_setting_group = RadioSettingGroup("mic_calibration",
                                                "Microphone sensitivity")
        calibration.append(radio_setting_group)

        for lvl in range(0, 5):
            name = "cal.micLevel[%s]" % lvl
            tempval = min_max_def(_mem.get_path(name), 0, 31, 31)
            val = RadioSettingValueInteger(0, 31, tempval)
            radio_setting = RadioSetting(name, "Level %i" % lvl, val)
            radio_setting_group.append(radio_setting)

        radio_setting_group = RadioSettingGroup("other_calibration", "Other")
        calibration.append(radio_setting_group)

        name = "cal.xtalFreqLow"
        temp_val = min_max_def(_mem.get_path(name), -1000, 1000, 0)
        val = RadioSettingValueInteger(-1000, 1000, temp_val)
        radio_setting = RadioSetting(name, "Xtal frequency low", val)
        radio_setting_group.append(radio_setting)

        name = "cal.volumeGain"
        temp_val = min_max_def(_mem.get_path(name), 0, 63, 58)
        val = RadioSettingValueInteger(0, 63, temp_val)
        radio_setting = RadioSetting(name, "Volume gain", val)
        radio_setting_group.append(radio_setting)

        name = "cal.dacGain"
        temp_val = min_max_def(_mem.get_path(name), 0, 15, 8)
        val = RadioSettingValueInteger(0, 15, temp_val)
        radio_setting = RadioSetting(name, "DAC gain", val)
        radio_setting_group.append(radio_setting)

        # -------- LAYOUT

        basic.append(squelch_setting)
        basic.append(rx_mode_setting)
        basic.append(call_channel_setting)
        basic.append(auto_keypad_lock_setting)
        basic.append(tx_t_out_setting)
        basic.append(bat_save_setting)
        basic.append(scn_rev_setting)
        if _mem.BUILD_OPTIONS.ENABLE_NOAA:
            basic.append(noaa_auto_scan_setting)
        if _mem.BUILD_OPTIONS.ENABLE_AM_FIX:
            basic.append(am_fix_setting)

        dispSubGrp = RadioSettingSubGroup("dispSubGrp", "Display settings")
        basic.append(dispSubGrp)
        dispSubGrp.append(bat_txt_setting)
        dispSubGrp.append(mic_bar_setting)
        dispSubGrp.append(ch_disp_setting)
        dispSubGrp.append(p_on_msg_setting)
        dispSubGrp.append(logo1_setting)
        dispSubGrp.append(logo2_setting)

        bcklSubGrp = RadioSettingSubGroup("bcklSubGrp", "Backlight settings")
        basic.append(bcklSubGrp)
        bcklSubGrp.append(back_lt_setting)
        bcklSubGrp.append(bl_min_setting)
        bcklSubGrp.append(bl_max_setting)
        bcklSubGrp.append(blt_trx_setting)

        audioSubGrp = RadioSettingSubGroup("audioSubGrp",
                                           "Audio related settings")
        basic.append(audioSubGrp)
        if _mem.BUILD_OPTIONS.ENABLE_VOX:
            audioSubGrp.append(vox_setting)
        audioSubGrp.append(mic_gain_setting)
        audioSubGrp.append(beep_setting)
        audioSubGrp.append(roger_setting)
        audioSubGrp.append(ste_setting)
        audioSubGrp.append(rp_ste_setting)
        if _mem.BUILD_OPTIONS.ENABLE_VOICE:
            audioSubGrp.append(voice_setting)
        if _mem.BUILD_OPTIONS.ENABLE_ALARM:
            audioSubGrp.append(alarm_setting)

        stateSubGrp = RadioSettingSubGroup("stateSubGrp", "Radio state")
        basic.append(stateSubGrp)
        stateSubGrp.append(freq0_setting)
        stateSubGrp.append(freq1_setting)
        stateSubGrp.append(tx_vfo_setting)
        stateSubGrp.append(keypad_cock_setting)

        advanced.append(freq_mode_allowed_setting)
        advanced.append(bat_type_setting)
        advanced.append(s0_level_setting)
        advanced.append(s9_level_setting)
        if _mem.BUILD_OPTIONS.ENABLE_PWRON_PASSWORD:
            advanced.append(pswd_setting)

        if _mem.BUILD_OPTIONS.ENABLE_DTMF_CALLING:
            dtmf.append(sep_code_setting)
            dtmf.append(group_code_setting)
        dtmf.append(first_code_per_setting)
        dtmf.append(spec_per_setting)
        dtmf.append(code_per_setting)
        dtmf.append(code_int_setting)
        if _mem.BUILD_OPTIONS.ENABLE_DTMF_CALLING:
            dtmf.append(ani_id_setting)
        dtmf.append(up_code_setting)
        dtmf.append(dw_code_setting)
        dtmf.append(d_prel_setting)
        dtmf.append(dtmf_side_tone_setting)
        if _mem.BUILD_OPTIONS.ENABLE_DTMF_CALLING:
            dtmf.append(dtmf_resp_setting)
            dtmf.append(d_hold_setting)
            dtmf.append(d_live_setting)
            dtmf.append(perm_kill_setting)
            dtmf.append(kill_code_setting)
            dtmf.append(rev_code_setting)
            dtmf.append(killed_setting)

        unlock.append(f_lock_setting)
        unlock.append(tx200_setting)
        unlock.append(tx350_setting)
        unlock.append(tx500_setting)
        unlock.append(en350_setting)
        unlock.append(en_scrambler_setting)

        return top

MEM_FORMAT3 = """
#seekto 0xe40;
ul16 fmfreq[20];

#seekto 0xe78;
u8 backlight_min:4,
backlight_max:4;

u8 channel_display_mode;
u8 crossband;
u8 battery_save;
u8 dual_watch;
u8 backlight_time;
u8 ste;
u8 freq_mode_allowed;

#seekto 0xe90;
u8 keyM_longpress_action:7,
    button_beep:1;

u8 key1_shortpress_action;
u8 key1_longpress_action;
u8 key2_shortpress_action;
u8 key2_longpress_action;
u8 scan_resume_mode;
u8 auto_keypad_lock;
u8 power_on_dispmode;
ul32 password;

#seekto 0xea0;
u8 voice;
u8 s0_level;
u8 s9_level;

#seekto 0xea8;
u8 alarm_mode;
u8 roger_beep;
u8 rp_ste;
u8 TX_VFO;
u8 Battery_type;

#seekto 0xeb0;
char logo_line1[16];
char logo_line2[16];

//#seekto 0xed0;
struct {
    u8 side_tone;
    char separate_code;
    char group_call_code;
    u8 decode_response;
    u8 auto_reset_time;
    u8 preload_time;
    u8 first_code_persist_time;
    u8 hash_persist_time;
    u8 code_persist_time;
    u8 code_interval_time;
    u8 permit_remote_kill;

    #seekto 0xee0;
    char local_code[3];
    #seek 5;
    char kill_code[5];
    #seek 3;
    char revive_code[5];
    #seek 3;
    char up_code[16];
    char down_code[16];
} dtmf;

#seekto 0xf40;
u8 int_flock;
u8 int_350tx;
u8 int_KILLED;
u8 int_200tx;
u8 int_500tx;
u8 int_350en;
u8 int_scren;


u8  backlight_on_TX_RX:2,
    AM_fix:1,
    mic_bar:1,
    battery_text:2,
    live_DTMF_decoder:1,
    unknown:1;


#seekto 0x1c00;
struct {
char name[8];
char number[3];
#seek 5;
} dtmfcontact[16];

struct {
    struct {
        #seekto 0x1E00;
        u8 openRssiThr[10];
        #seekto 0x1E10;
        u8 closeRssiThr[10];
        #seekto 0x1E20;
        u8 openNoiseThr[10];
        #seekto 0x1E30;
        u8 closeNoiseThr[10];
        #seekto 0x1E40;
        u8 closeGlitchThr[10];
        #seekto 0x1E50;
        u8 openGlitchThr[10];
    } sqlBand4_7;

    struct {
        #seekto 0x1E60;
        u8 openRssiThr[10];
        #seekto 0x1E70;
        u8 closeRssiThr[10];
        #seekto 0x1E80;
        u8 openNoiseThr[10];
        #seekto 0x1E90;
        u8 closeNoiseThr[10];
        #seekto 0x1EA0;
        u8 closeGlitchThr[10];
        #seekto 0x1EB0;
        u8 openGlitchThr[10];
    } sqlBand1_3;

    #seekto 0x1EC0;
    struct {
        ul16 level1;
        ul16 level2;
        ul16 level4;
        ul16 level6;
    } rssiLevelsBands3_7;

    struct {
        ul16 level1;
        ul16 level2;
        ul16 level4;
        ul16 level6;
    } rssiLevelsBands1_2;

    struct {
        struct {
            u8 lower;
            u8 center;
            u8 upper;
        } low;
        struct {
            u8 lower;
            u8 center;
            u8 upper;
        } mid;
        struct {
            u8 lower;
            u8 center;
            u8 upper;
        } hi;
        #seek 7;
    } txp[7];

    #seekto 0x1F40;
    ul16 batLvl[6];

    #seekto 0x1F50;
    ul16 vox1Thr[10];

    #seekto 0x1F68;
    ul16 vox0Thr[10];

    #seekto 0x1F80;
    u8 micLevel[5];

    #seekto 0x1F88;
    il16 xtalFreqLow;

    #seekto 0x1F8E;
    u8 volumeGain;
    u8 dacGain;
} cal;


#seekto 0x1FF0;
struct {
u8 ENABLE_DTMF_CALLING:1,
   ENABLE_PWRON_PASSWORD:1,
   ENABLE_TX1750:1,
   ENABLE_ALARM:1,
   ENABLE_VOX:1,
   ENABLE_VOICE:1,
   ENABLE_NOAA:1,
   ENABLE_FMRADIO:1;
u8 __UNUSED:3,
   ENABLE_AM_FIX:1,
   ENABLE_BLMIN_TMP_OFF:1,
   ENABLE_RAW_DEMODULATORS:1,
   ENABLE_WIDE_RX:1,
   ENABLE_FLASHLIGHT:1;
} BUILD_OPTIONS;


// 0x0E80 EEPROM_DISP_CH_STORE_OFF
#seekto 0x2000;
u16 ScreenChannel_A;
u16 MrChannel_A;
u16 FreqChannel_A;
u16 ScreenChannel_B;
u16 MrChannel_B;
u16 FreqChannel_B;
u16 NoaaChannel_A;
u16 NoaaChannel_B;

// 0x0E70 EEPROM_SETTINGS_OFF
//#seekto 0x2010;
u16 call_channel;
u16 squelch;
u16 max_talk_time;
u16 noaa_autoscan;
u16 key_lock;
u16 vox_switch;
u16 vox_level;
u16 mic_gain;

// 0x0E70 EEPROM_SCANLIST_OFF
//#seekto 0x2020;
u16 slDef;
u16 sl1PriorEnab;
u16 sl1PriorCh1;
u16 sl1PriorCh2;
u16 sl2PriorEnab;
u16 sl2PriorCh1;
u16 sl2PriorCh2;
//u16 unused

// 0x0F50 EEPROM_MR_CH_NAME_OFF
#seekto 0x2030;
struct {
    char name[16];
// channels
} channelname[999];

// 0x0000 EEPROM_MR_CH_FREQ_OFF
// 0x0C80 EEPROM_FREQ_CH_FREQ_OFF
//#seekto 0x5ea0;
struct {
  ul32 freq;
  ul32 offset;

// 0x08
  u8 rxcode;
  u8 txcode;

// 0x0A
  u8 txcodeflag:4,
  rxcodeflag:4;

// 0x0B
  u8 modulation:4,
  shift:4;

// 0x0C
  u8 __UNUSED1:3,
  bclo:1,
  txpower:2,
  bandwidth:1,
  freq_reverse:1;

  // 0x0D
  u8 __UNUSED2:4,
  dtmf_pttid:3,
  dtmf_decode:1;

  // 0x0E
  u8 step;
  u8 scrambler;
// channels + 14
} channel[1013];

// 0x0D60 EEPROM_MR_CH_ATTR_OFF
// 0x0E28 EEPROM_FREQ_CH_ATTR_OFF
//#seekto 0x0df0;
struct {
  u8 is_scanlist1:1,
  is_scanlist2:1,
  compander:2,
  is_free:1,
   band:3;
// channels + 7
} channel_attributes[1006];
"""


@directory.register
@directory.detected_by(UVK5Radio)
class UVK5RadioEgzumer999(UVK5RadioEgzumerMod):
    """Quansheng UV-K5 (egzumer) 999 channels"""
    VENDOR = "Quansheng"
    MODEL = "UV-K5"
    VARIANT = "AT999V1"
    BAUD_RATE = 38400
    NEEDS_COMPAT_SERIAL = False
    FIRMWARE_VERSION = ""
    _mem_size = 0x10000 # eeprom total size
    _prog_size = 0x10000 # eeprom size without calibration
    _channels = 999  # number of MR channels
    _channels_mask = 0xffff  # max channel number
    _upload_calibration = False

    @classmethod
    def k5_approve_firmware(cls, firmware):
        return firmware.startswith('AT999V1 ')
    
    # Convert the raw byte array into a memory object structure
    def process_mmap(self):
        self._check_firmware_at_load()
        self._memobj = bitwise.parse(MEM_FORMAT3, self._mmap)

MEM_FORMAT2 = """
#seekto 0xe40;
ul16 fmfreq[20];

#seekto 0xe78;
u8 backlight_min:4,
backlight_max:4;

u8 channel_display_mode;
u8 crossband;
u8 battery_save;
u8 dual_watch;
u8 backlight_time;
u8 ste;
u8 freq_mode_allowed;

#seekto 0xe90;
u8 keyM_longpress_action:7,
    button_beep:1;

u8 key1_shortpress_action;
u8 key1_longpress_action;
u8 key2_shortpress_action;
u8 key2_longpress_action;
u8 scan_resume_mode;
u8 auto_keypad_lock;
u8 power_on_dispmode;
ul32 password;

#seekto 0xea0;
u8 voice;
u8 s0_level;
u8 s9_level;

#seekto 0xea8;
u8 alarm_mode;
u8 roger_beep;
u8 rp_ste;
u8 TX_VFO;
u8 Battery_type;

#seekto 0xeb0;
char logo_line1[16];
char logo_line2[16];

//#seekto 0xed0;
struct {
    u8 side_tone;
    char separate_code;
    char group_call_code;
    u8 decode_response;
    u8 auto_reset_time;
    u8 preload_time;
    u8 first_code_persist_time;
    u8 hash_persist_time;
    u8 code_persist_time;
    u8 code_interval_time;
    u8 permit_remote_kill;

    #seekto 0xee0;
    char local_code[3];
    #seek 5;
    char kill_code[5];
    #seek 3;
    char revive_code[5];
    #seek 3;
    char up_code[16];
    char down_code[16];
} dtmf;

#seekto 0xf40;
u8 int_flock;
u8 int_350tx;
u8 int_KILLED;
u8 int_200tx;
u8 int_500tx;
u8 int_350en;
u8 int_scren;


u8  backlight_on_TX_RX:2,
    AM_fix:1,
    mic_bar:1,
    battery_text:2,
    live_DTMF_decoder:1,
    unknown:1;


#seekto 0x1c00;
struct {
char name[8];
char number[3];
#seek 5;
} dtmfcontact[16];

struct {
    struct {
        #seekto 0x1E00;
        u8 openRssiThr[10];
        #seekto 0x1E10;
        u8 closeRssiThr[10];
        #seekto 0x1E20;
        u8 openNoiseThr[10];
        #seekto 0x1E30;
        u8 closeNoiseThr[10];
        #seekto 0x1E40;
        u8 closeGlitchThr[10];
        #seekto 0x1E50;
        u8 openGlitchThr[10];
    } sqlBand4_7;

    struct {
        #seekto 0x1E60;
        u8 openRssiThr[10];
        #seekto 0x1E70;
        u8 closeRssiThr[10];
        #seekto 0x1E80;
        u8 openNoiseThr[10];
        #seekto 0x1E90;
        u8 closeNoiseThr[10];
        #seekto 0x1EA0;
        u8 closeGlitchThr[10];
        #seekto 0x1EB0;
        u8 openGlitchThr[10];
    } sqlBand1_3;

    #seekto 0x1EC0;
    struct {
        ul16 level1;
        ul16 level2;
        ul16 level4;
        ul16 level6;
    } rssiLevelsBands3_7;

    struct {
        ul16 level1;
        ul16 level2;
        ul16 level4;
        ul16 level6;
    } rssiLevelsBands1_2;

    struct {
        struct {
            u8 lower;
            u8 center;
            u8 upper;
        } low;
        struct {
            u8 lower;
            u8 center;
            u8 upper;
        } mid;
        struct {
            u8 lower;
            u8 center;
            u8 upper;
        } hi;
        #seek 7;
    } txp[7];

    #seekto 0x1F40;
    ul16 batLvl[6];

    #seekto 0x1F50;
    ul16 vox1Thr[10];

    #seekto 0x1F68;
    ul16 vox0Thr[10];

    #seekto 0x1F80;
    u8 micLevel[5];

    #seekto 0x1F88;
    il16 xtalFreqLow;

    #seekto 0x1F8E;
    u8 volumeGain;
    u8 dacGain;
} cal;


#seekto 0x1FF0;
struct {
u8 ENABLE_DTMF_CALLING:1,
   ENABLE_PWRON_PASSWORD:1,
   ENABLE_TX1750:1,
   ENABLE_ALARM:1,
   ENABLE_VOX:1,
   ENABLE_VOICE:1,
   ENABLE_NOAA:1,
   ENABLE_FMRADIO:1;
u8 __UNUSED:3,
   ENABLE_AM_FIX:1,
   ENABLE_BLMIN_TMP_OFF:1,
   ENABLE_RAW_DEMODULATORS:1,
   ENABLE_WIDE_RX:1,
   ENABLE_FLASHLIGHT:1;
} BUILD_OPTIONS;


// 0x0E80 EEPROM_DISP_CH_STORE_OFF
#seekto 0x2000;
u16 ScreenChannel_A;
u16 MrChannel_A;
u16 FreqChannel_A;
u16 ScreenChannel_B;
u16 MrChannel_B;
u16 FreqChannel_B;
u16 NoaaChannel_A;
u16 NoaaChannel_B;

// 0x0E70 EEPROM_SETTINGS_OFF
//#seekto 0x2010;
u16 call_channel;
u16 squelch;
u16 max_talk_time;
u16 noaa_autoscan;
u16 key_lock;
u16 vox_switch;
u16 vox_level;
u16 mic_gain;

// 0x0E70 EEPROM_SCANLIST_OFF
//#seekto 0x2020;
u16 slDef;
u16 sl1PriorEnab;
u16 sl1PriorCh1;
u16 sl1PriorCh2;
u16 sl2PriorEnab;
u16 sl2PriorCh1;
u16 sl2PriorCh2;
//u16 unused

// 0x0F50 EEPROM_MR_CH_NAME_OFF
#seekto 0x2030;
struct {
    char name[16];
// channels
} channelname[736];

// 0x0000 EEPROM_MR_CH_FREQ_OFF
// 0x0C80 EEPROM_FREQ_CH_FREQ_OFF
//#seekto 0x4e30;
struct {
  ul32 freq;
  ul32 offset;

// 0x08
  u8 rxcode;
  u8 txcode;

// 0x0A
  u8 txcodeflag:4,
  rxcodeflag:4;

// 0x0B
  u8 modulation:4,
  shift:4;

// 0x0C
  u8 __UNUSED1:3,
  bclo:1,
  txpower:2,
  bandwidth:1,
  freq_reverse:1;

  // 0x0D
  u8 __UNUSED2:4,
  dtmf_pttid:3,
  dtmf_decode:1;

  // 0x0E
  u8 step;
  u8 scrambler;
// channels + 14
} channel[750];

// 0x0D60 EEPROM_MR_CH_ATTR_OFF
// 0x0E28 EEPROM_FREQ_CH_ATTR_OFF
//#seekto 0x7d70;
struct {
  u8 is_scanlist1:1,
  is_scanlist2:1,
  compander:2,
  is_free:1,
   band:3;
// channels + 7
} channel_attributes[743];
"""


@directory.register
@directory.detected_by(UVK5Radio)
class UVK5RadioEgzumer736(UVK5RadioEgzumerMod):
    """Quansheng UV-K5 (egzumer) 736 channels"""
    VENDOR = "Quansheng"
    MODEL = "UV-K5"
    VARIANT = "AT736V1"
    BAUD_RATE = 38400
    NEEDS_COMPAT_SERIAL = False
    FIRMWARE_VERSION = ""
    _mem_size = 0x8000 # eeprom total size
    _prog_size = 0x8000 # eeprom size without calibration
    _channels = 736  # number of MR channels
    _channels_mask = 0xffff  # max channel number

    @classmethod
    def k5_approve_firmware(cls, firmware):
        return firmware.startswith('AT736V1 ')
    
    # Convert the raw byte array into a memory object structure
    def process_mmap(self):
        self._check_firmware_at_load()
        self._memobj = bitwise.parse(MEM_FORMAT2, self._mmap)
        
MEM_FORMAT1 = """
#seekto 0xe40;
ul16 fmfreq[20];

#seekto 0xe78;
u8 backlight_min:4,
backlight_max:4;

u8 channel_display_mode;
u8 crossband;
u8 battery_save;
u8 dual_watch;
u8 backlight_time;
u8 ste;
u8 freq_mode_allowed;

#seekto 0xe90;
u8 keyM_longpress_action:7,
    button_beep:1;

u8 key1_shortpress_action;
u8 key1_longpress_action;
u8 key2_shortpress_action;
u8 key2_longpress_action;
u8 scan_resume_mode;
u8 auto_keypad_lock;
u8 power_on_dispmode;
ul32 password;

#seekto 0xea0;
u8 voice;
u8 s0_level;
u8 s9_level;

#seekto 0xea8;
u8 alarm_mode;
u8 roger_beep;
u8 rp_ste;
u8 TX_VFO;
u8 Battery_type;

#seekto 0xeb0;
char logo_line1[16];
char logo_line2[16];

//#seekto 0xed0;
struct {
    u8 side_tone;
    char separate_code;
    char group_call_code;
    u8 decode_response;
    u8 auto_reset_time;
    u8 preload_time;
    u8 first_code_persist_time;
    u8 hash_persist_time;
    u8 code_persist_time;
    u8 code_interval_time;
    u8 permit_remote_kill;

    #seekto 0xee0;
    char local_code[3];
    #seek 5;
    char kill_code[5];
    #seek 3;
    char revive_code[5];
    #seek 3;
    char up_code[16];
    char down_code[16];
} dtmf;

#seekto 0xf40;
u8 int_flock;
u8 int_350tx;
u8 int_KILLED;
u8 int_200tx;
u8 int_500tx;
u8 int_350en;
u8 int_scren;


u8  backlight_on_TX_RX:2,
    AM_fix:1,
    mic_bar:1,
    battery_text:2,
    live_DTMF_decoder:1,
    unknown:1;


#seekto 0x1c00;
struct {
char name[8];
char number[3];
#seek 5;
} dtmfcontact[16];

struct {
    struct {
        #seekto 0x1E00;
        u8 openRssiThr[10];
        #seekto 0x1E10;
        u8 closeRssiThr[10];
        #seekto 0x1E20;
        u8 openNoiseThr[10];
        #seekto 0x1E30;
        u8 closeNoiseThr[10];
        #seekto 0x1E40;
        u8 closeGlitchThr[10];
        #seekto 0x1E50;
        u8 openGlitchThr[10];
    } sqlBand4_7;

    struct {
        #seekto 0x1E60;
        u8 openRssiThr[10];
        #seekto 0x1E70;
        u8 closeRssiThr[10];
        #seekto 0x1E80;
        u8 openNoiseThr[10];
        #seekto 0x1E90;
        u8 closeNoiseThr[10];
        #seekto 0x1EA0;
        u8 closeGlitchThr[10];
        #seekto 0x1EB0;
        u8 openGlitchThr[10];
    } sqlBand1_3;

    #seekto 0x1EC0;
    struct {
        ul16 level1;
        ul16 level2;
        ul16 level4;
        ul16 level6;
    } rssiLevelsBands3_7;

    struct {
        ul16 level1;
        ul16 level2;
        ul16 level4;
        ul16 level6;
    } rssiLevelsBands1_2;

    struct {
        struct {
            u8 lower;
            u8 center;
            u8 upper;
        } low;
        struct {
            u8 lower;
            u8 center;
            u8 upper;
        } mid;
        struct {
            u8 lower;
            u8 center;
            u8 upper;
        } hi;
        #seek 7;
    } txp[7];

    #seekto 0x1F40;
    ul16 batLvl[6];

    #seekto 0x1F50;
    ul16 vox1Thr[10];

    #seekto 0x1F68;
    ul16 vox0Thr[10];

    #seekto 0x1F80;
    u8 micLevel[5];

    #seekto 0x1F88;
    il16 xtalFreqLow;

    #seekto 0x1F8E;
    u8 volumeGain;
    u8 dacGain;
} cal;


#seekto 0x1FF0;
struct {
u8 ENABLE_DTMF_CALLING:1,
   ENABLE_PWRON_PASSWORD:1,
   ENABLE_TX1750:1,
   ENABLE_ALARM:1,
   ENABLE_VOX:1,
   ENABLE_VOICE:1,
   ENABLE_NOAA:1,
   ENABLE_FMRADIO:1;
u8 __UNUSED:3,
   ENABLE_AM_FIX:1,
   ENABLE_BLMIN_TMP_OFF:1,
   ENABLE_RAW_DEMODULATORS:1,
   ENABLE_WIDE_RX:1,
   ENABLE_FLASHLIGHT:1;
} BUILD_OPTIONS;


// 0x0E80 EEPROM_DISP_CH_STORE_OFF
#seekto 0x2000;
u16 ScreenChannel_A;
u16 MrChannel_A;
u16 FreqChannel_A;
u16 ScreenChannel_B;
u16 MrChannel_B;
u16 FreqChannel_B;
u16 NoaaChannel_A;
u16 NoaaChannel_B;

// 0x0E70 EEPROM_SETTINGS_OFF
//#seekto 0x2010;
u16 call_channel;
u16 squelch;
u16 max_talk_time;
u16 noaa_autoscan;
u16 key_lock;
u16 vox_switch;
u16 vox_level;
u16 mic_gain;

// 0x0E70 EEPROM_SCANLIST_OFF
//#seekto 0x2020;
u16 slDef;
u16 sl1PriorEnab;
u16 sl1PriorCh1;
u16 sl1PriorCh2;
u16 sl2PriorEnab;
u16 sl2PriorCh1;
u16 sl2PriorCh2;
//u16 unused

// 0x0F50 EEPROM_MR_CH_NAME_OFF
#seekto 0x2030;
struct {
    char name[16];
// channels
} channelname[239];

// 0x0000 EEPROM_MR_CH_FREQ_OFF
// 0x0C80 EEPROM_FREQ_CH_FREQ_OFF
//#seekto 0x4e30;
struct {
  ul32 freq;
  ul32 offset;

// 0x08
  u8 rxcode;
  u8 txcode;

// 0x0A
  u8 txcodeflag:4,
  rxcodeflag:4;

// 0x0B
  u8 modulation:4,
  shift:4;

// 0x0C
  u8 __UNUSED1:3,
  bclo:1,
  txpower:2,
  bandwidth:1,
  freq_reverse:1;

  // 0x0D
  u8 __UNUSED2:4,
  dtmf_pttid:3,
  dtmf_decode:1;

  // 0x0E
  u8 step;
  u8 scrambler;
// channels + 14
} channel[253];

// 0x0D60 EEPROM_MR_CH_ATTR_OFF
// 0x0E28 EEPROM_FREQ_CH_ATTR_OFF
//#seekto 0x7d70;
struct {
  u8 is_scanlist1:1,
  is_scanlist2:1,
  compander:2,
  is_free:1,
   band:3;
// channels + 7
} channel_attributes[246];
"""


@directory.register
@directory.detected_by(UVK5Radio)
class UVK5RadioEgzumer239(UVK5RadioEgzumerMod):
    """Quansheng UV-K5 (egzumer) 239 channels"""
    VENDOR = "Quansheng"
    MODEL = "UV-K5"
    VARIANT = "AT239V1"
    BAUD_RATE = 38400
    NEEDS_COMPAT_SERIAL = False
    FIRMWARE_VERSION = ""
    _mem_size = 0x4000 # eeprom total size
    _prog_size = 0x4000 # eeprom size without calibration
    _channels = 239  # number of MR channels
    _channels_mask = 0xffff  # max channel number

    @classmethod
    def k5_approve_firmware(cls, firmware):
        return firmware.startswith('AT239V1 ')
    
    # Convert the raw byte array into a memory object structure
    def process_mmap(self):
        self._check_firmware_at_load()
        self._memobj = bitwise.parse(MEM_FORMAT1, self._mmap)

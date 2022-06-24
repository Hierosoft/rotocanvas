# FFmpeg Notes
These features may be added to the python module at some point, but for
now you can do them manually
(See also "more" folder in [RotoCanvasPaint](https://github.com/poikilos/RotoCanvasPaint) and
[IntroCompatiblizer](https://github.com/poikilos/IntroCompatiblizer)).
- For a program that has a narrow use case but has additional video
  conversion commands embedded in the Python code as strings, see
  <https://github.com/poikilos/IntroCompatiblizer>.
- Combine videos (this is a one-line command, however, text file works
  better for some reason--see <http://www.github.com/poikilos/IntroCompatiblizer>)
  `ffmpeg -i "concat:Logo4 Animation A 1a0001-0100.avi|Logo4 Animation A 1a101-142.avi" -c copy "Logo4 Animation A 1a combined.avi"`
  * Even with text file, the names may need to be changed automatically
    first to prevent ffmpeg syntax error.
- h.264 avi to mp3 container for Sony software
  `ffmpeg -i "Logo4 Animation A 1b.avi" -acodec libfaac -b:a 128k -vcodec mpeg4 -b:v 1200k -flags +aic+mv4 "Logo4 Animation A 1b.mp4"`
- losslessly split
  `ffmpeg -vcodec copy -acodec copy -ss 00:00:00 -t 00:01:00 -i in.mp4 out.mp4`
  * where time after ss is start as hh:mm:ss, & time after t is duration as hh:mm:ss.
- losslessly change container e.g. from FLV to MP4:
  `ffmpeg -i VideoFile.flv -vcodec copy -acodec copy VideoFile.mp4`
  * allows Premiere Elements to load it (tested where flv was AVC video with AAC audio)
- convert video to image sequence:
  `ffmpeg -i VideoFile.m2v Forensics1a%d.png`
- convert image sequence to video:
  * Tried with image sequence in folder: $HOME\Videos\Projects\Rebel Assault IX\RAIX2b\Scene07 (Lightsaber Duel)\forcegrab\2b4 (2013 3D Hilt flying away and back added)\
  * Force fps such as 29.97: `ffmpeg -r 29.97 -i RAIX2b4-scene-lightsaberduel-shot-forcegrab%04d.png -sameq -r 29.97 output.mp4`
    * #-r forces frame rate to same so no frames are skipped (default is 25 fps, so, for example, converting to 24fps results in 1 lost per second)
      * [failed]ffmpeg -f image2 -i RAIX2b4-scene-lightsaberduel-shot-forcegrab%04d.png VideoFile.mpg
        * NOTE: only failed since "truncated or corrupted" input error occurred, due to using %d when %04d was required (for 4-digit 0-padded frame numbering)
      * [failed]ffmpeg -f png -i RAIX2b4-scene-lightsaberduel-shot-forcegrab%04d.png input -acodec aac -ab 128kb -vcodec mpeg4 -b 1200kb -mbd 2 -flags +4mv+trell -aic 2 -cmp 2 -subcmp 2 -title X final_video.mp4
        * NOTE: only failed since "truncated or corrupted" input error occurred, due to using %d when %04d was required (for 4-digit 0-padded frame numbering)
      * or for iPod:
        * [failed]ffmpeg -f image2 -i RAIX2b4-scene-lightsaberduel-shot-forcegrab%04d.png input -acodec aac -ab 128kb -vcodec mpeg4 -b 1200kb -mbd 2 -flags +4mv+trell -aic 2 -cmp 2 -subcmp 2 -s 320x180 -title X output-ipod.mp4
          * for older ffmpeg only
        * [failed]ffmpeg -r 29.97 -f image2 -i RAIX2b4-scene-lightsaberduel-shot-forcegrab%04d.png -r 29.97 -acodec aac -ab 128k -vcodec mpeg4 -b 1200k -mbd 2 -flags +mv4+aic -trellis 1 -cmp 2 -subcmp 2 -s 320x180 -metadata title=X output-ipod.mp4
          * didn't accept metadata option
        * `ffmpeg -r 29.97 -f image2 -i RAIX2b4-scene-lightsaberduel-shot-forcegrab%04d.png -r 29.97 -acodec aac -ab 128k -vcodec mpeg4 -b 1200k -mbd 2 -flags +mv4+aic -trellis 1 -cmp 2 -subcmp 2 -s 320x180 -metadata title=X output-ipod.mp4`
      * or for YouTube:
        * [failed]ffmpeg -r 30 -i RAIX2b4-scene-lightsaberduel-shot-forcegrab%04d.png -s:v 1280x720 -c:v libx264 -profile:v high -crf 23 -pix_fmt yuv420p -r 30 output-YouTube.mp4
- convert to m2ts (from IntegratorEduImport):
(see also "Selecting codecs and container formats." mplayer.hu. <http://www.mplayerhq.hu/DOCS/HTML/en/menc-feat-selecting-codec.html>. Oct 11, 2012.)
```batch
REM Convert to m2ts (tried using mencoder):
REM mencoder -of help doesn't list mts, only mpeg (MPEG-1&MPEG-2 PS according to mplayerhq.hu), xvid (MPEG-4 ASP), and x264 (MPEG-4 AVC)
REM lavf means that you then specify a libavformat container -- still only has mpg (MPEG-1&MPEG-2 PS according to mplayerhq.hu) & mp4
REM mencoder was originally only meant for AVI so resulting file should be tested, according to mplayerhq.hu
REM mencoder 00394.mts -vf scale=1280:720 -oac copy -fps 60 -ofps 30 -o %USERPROFILE%\Documents\1080-to-720-00394.m2ts
REM mencoder 00394.mts -s hd720 -oac copy -fps 60 -ofps 30 -o %USERPROFILE%\Documents\1080-to-720-00394.m2ts
```
- ffmpeg convert h.264 avi to mp4 container for sony
  `ffmpeg -i "Logo4 Animation A 1b.avi" -acodec libfaac -b:a 128k -vcodec mpeg4 -b:v 1200k -flags +aic+mv4 "Logo4 Animation A 1b.mp4"`
  * Convert to m2ts (using ffmpeg):
    * -y overwrite output files without asking
    * -loglevel 1  is OK too
    * -r doesn't seem to work before input (for forcing framerate)
    * -qscale is deprecated -- says to use -q:v (quantize video) or -q:a (quantize audio) instead
    * "-async <samples per second> to resync audio is deprecated, use asyncts instead"
    * `ffmpeg -y -r 60 -i "00394.mts" -r 30 -aspect 16:9 -qscale 4 -vcodec mpeg2video -acodec copy -f mpegts "%USERPROFILE%\Documents\1080-to-720-00394.m2ts"`
    * `ffmpeg -y -i "00394.mts" -r 30 -s 1280x720 -qscale 4 -vcodec mpeg2video -acodec copy -f mpegts "%USERPROFILE%\Documents\1080-to-720-00394.m2ts"`

- Resize (-s: Scale) mpeg2ts video such as from Canon VIXIA HF G10:
  - `ffmpeg -y -i "00394.mts" -r 30 -s 1280x720 -q:v 4 -vcodec mpeg2video -acodec copy -f mpegts "%USERPROFILE%\Documents\1080-to-720-00394.m2ts"`

- dump sound losslessly:
```bash
  #PART OF SOUND e.g. 1st minute ffmpeg -vcodec copy -acodec copy -s 00:00:00 -t 00:01:00 -i in.flv intro-only1a_480p.flv
  #If multiple audio streams or audio not detected, first get Audio ID: ffmpeg -i "$filename"
  ffmpeg -i "$vidbasename.mp4" -vn -f wav "$vidbasename-audio.wav"
  ffmpeg -i "$vidbasename.mp4" -vn -acodec copy "$vidbasename-audio.m4a"
  ffmpeg -i "$vidbasename.flv" -vn -acodec copy "$vidbasename-audio.mp3"
  #   - where .mp3 a compatible container e.g.:
  #    ffmpeg -i "$vidbasename.ogg" -acodec copy "$vidbasename.mkv"
  #some people do:
  ffmpeg -i video.mpg -acodec copy audio.ac3
  mplayer x.mpg -dumpaudio -dumpfile sound.ac3
  mplayer source_file.vob -aid 129 -dumpaudio -dumpfile sound.ac3
  #  - where 129 is the audio id
```
- extract and recompress incompatible ac3 or other audio stream (allow burning video+audio with Sony DVD Architect; works with wave file input too):
```
  ffmpeg -i video.mpg -ab 224k -ar 48000 -ac 2 -acodec ac3 video.ac3
```
- extract and compress sound:
```
  ffmpeg -i "$vidbasename.mp4" -vn -ar 44100 -ac 2 -ab 192 -f mp3 "$vidbasename-audio.mp3"
```
- Edit video:
  * Split file: `ffmpeg -vcodec copy -ss 00:01:00 -t 00:03:00 -i infile.mpg outfile.mpg`
- Extract from DVD losslessly (not encrypted dvds):
```bash
#ffmpeg -i concat:'VTS_01_1.VOB|VTS_01_2.VOB|VTS_01_3.VOB|VTS_01_4.VOB|VTS_01_5.VOB|VTS_01_6.VOB|VTS_01_7.VOB|VTS_01_8.VOB|VTS_01_9.VOB' -c copy $dest_path/Hi-8-to-DVD-via-Sharp.mpg
#the commands below supposedly also work
#ffmpeg -i 'concat:VTS_01_1.VOB|VTS_01_2.VOB|VTS_01_3.VOB|VTS_01_4.VOB|VTS_01_5.VOB|VTS_01_6.VOB|VTS_01_7.VOB|VTS_01_8.VOB|VTS_01_9.VOB' -c copy $dest_path/Hi-8-to-DVD-via-Sharp.mpg
#ffmpeg -i VTS_01_1.VOB -i VTS_01_2.VOB -i VTS_01_3.VOB -i VTS_01_4.VOB -i VTS_01_5.VOB -i VTS_01_6.VOB -i VTS_01_7.VOB -i VTS_01_8.VOB -i VTS_01_9.VOB -c copy $dest_path/Hi-8-to-DVD-via-Sharp.mpg
```
The commands above produce out-of-order errors due to timestamps starting at 0 at each file
so instead, as per <https://stackoverflow.com/questions/31691943/ffmpeg-concat-poduces-dts-out-of-order-errors> do:
```bash
#ffmpeg -i concat:'VTS_01_1.VOB|VTS_01_2.VOB|VTS_01_3.VOB|VTS_01_4.VOB|VTS_01_5.VOB|VTS_01_6.VOB|VTS_01_7.VOB|VTS_01_8.VOB|VTS_01_9.VOB' -c:v copy -c:a copy $dest_path/Hi-8-to-DVD-via-Sharp.mpg

dest_path=$HOME/Videos/OldFHC,The2017Repair/Media
vid_name=OldFHC,The3a
concat_list=concat.txt
cd /run/media/$USER
cd DVD*
cd VIDEO_TS
#NOTE: if extension is mpg, warning is shown: ac3 in MPEG-1 system streams is not widely supported, consider using the vob or the dvd muxer to force a MPEG-2 program stream.
#echo "file `pwd`/VTS_01_1.VOB" > $dest_path/$concat_list
#echo "file `pwd`/VTS_01_2.VOB" >> $dest_path/$concat_list
#echo "file `pwd`/VTS_01_3.VOB" >> $dest_path/$concat_list
#echo "file `pwd`/VTS_01_4.VOB" >> $dest_path/$concat_list
#echo "file `pwd`/VTS_01_5.VOB" >> $dest_path/$concat_list
#echo "file `pwd`/VTS_01_6.VOB" >> $dest_path/$concat_list
#echo "file `pwd`/VTS_01_7.VOB" >> $dest_path/$concat_list
#echo "file `pwd`/VTS_01_8.VOB" >> $dest_path/$concat_list
#echo "file `pwd`/VTS_01_9.VOB" >> $dest_path/$concat_list
#echo "file VTS_01_1.VOB" > $dest_path/$concat_list
#echo "file VTS_01_2.VOB" >> $dest_path/$concat_list
#echo "file VTS_01_3.VOB" >> $dest_path/$concat_list
#echo "file VTS_01_4.VOB" >> $dest_path/$concat_list
#echo "file VTS_01_5.VOB" >> $dest_path/$concat_list
#echo "file VTS_01_6.VOB" >> $dest_path/$concat_list
#echo "file VTS_01_7.VOB" >> $dest_path/$concat_list
#echo "file VTS_01_8.VOB" >> $dest_path/$concat_list
#echo "file VTS_01_9.VOB" >> $dest_path/$concat_list

#ffmpeg -i VTS_01_1.VOB -c copy -f dvd $dest_path/$vid_name-1of9.mpg
#ffmpeg -i VTS_01_2.VOB -c copy -f dvd $dest_path/$vid_name-2of9.mpg
#ffmpeg -i VTS_01_3.VOB -c copy -f dvd $dest_path/$vid_name-3of9.mpg
#ffmpeg -i VTS_01_4.VOB -c copy -f dvd $dest_path/$vid_name-4of9.mpg
#ffmpeg -i VTS_01_5.VOB -c copy -f dvd $dest_path/$vid_name-5of9.mpg
#ffmpeg -i VTS_01_6.VOB -c copy -f dvd $dest_path/$vid_name-6of9.mpg
#ffmpeg -i VTS_01_7.VOB -c copy -f dvd $dest_path/$vid_name-7of9.mpg
#ffmpeg -i VTS_01_8.VOB -c copy -f dvd $dest_path/$vid_name-8of9.mpg
#ffmpeg -i VTS_01_9.VOB -c copy -f dvd $dest_path/$vid_name-9of9.mpg
#not sure how to use -f mpegps in the following line but that may help according to https://lists.libav.org/pipermail/libav-bugs/2015-September/004286.html
#ffmpeg -f concat -safe 0 -i $dest_path/$concat_list -c copy -fflags +genpts -f dvd $dest_path/$vid_name.mpg
#-safe 0 is needed if using absolute paths (however, relative paths are relative to txt file so that may be difficult/impossible if source is readonly)
#see also https://superuser.com/questions/1150276/trim-video-and-concatenate-using-ffmpeg-getting-non-monotonous-dts-in-output
#ffmpeg -f concat -i $concat_list -c copy output.MTS
#where mylist must have lines like "file filename.MTS" (must have the word 'file')
#above results in faulty timecodes--file won't play back and doesn't have correct length, so...
#see https://wiki.archlinux.org/index.php/dvdbackup#Ripping_the_DVD:
cat VTS_01_*.VOB > $dest_path/$vid_name.VOB
#-y: overwrite
#(added -f dvd though to avoid MPEG-1 and therefore missing AC3 audio)
ffmpeg -y -i $dest_path/$vid_name.VOB -codec:v copy -codec:a copy -f dvd $dest_path/$vid_name.mpeg
#or see https://www.linuxquestions.org/questions/linux-software-2/ffmpeg-trying-to-demux-vob-subtitles-show-up-in-video-stream-785500/:
#mencoder $dest_path/$vid_name.VOB -ovc copy -of rawvideo -nosound -o $dest_path/$vid_name-via-mencoder.mpeg
#or see https://video.stackexchange.com/questions/3187/fix-timecode-in-merged-vobs:
#avconv -i $dest_path/$vid_name.VOB -vf 'setpts=PTS-STARTPTS' -c:a copy -c:v copy $dest_path/$vid_name-repaired-by-mencoder.vob
```

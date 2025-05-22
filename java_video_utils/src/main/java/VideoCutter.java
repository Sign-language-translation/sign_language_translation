import org.jcodec.api.FrameGrab;
import org.jcodec.api.SequenceEncoder;
import org.jcodec.common.io.NIOUtils;
import org.jcodec.common.model.Picture;
import org.jcodec.common.model.Rational;
import org.jcodec.common.model.Size;
import org.jcodec.common.FileChannelWrapper;

import java.io.File;
import java.io.IOException;

public class VideoCutter {

    /**
     * Cuts an MP4 video between two times (in seconds).
     *
     * @param inputPath  Path to input video (MP4 format)
     * @param outputPath Path to save the cut video
     * @param startSec   Start time in seconds (e.g. 5.0)
     * @param endSec     End time in seconds (e.g. 15.0)
     */
    public static void cutMp4(String inputPath, String outputPath, double startSec, double endSec) throws IOException {
        File inputFile = new File(inputPath);
        FileChannelWrapper inChannel = NIOUtils.readableChannel(inputFile);

        FrameGrab grab = FrameGrab.createFrameGrab(inChannel);
        grab.seekToSecondPrecise(startSec);

        File outputFile = new File(outputPath);
        SequenceEncoder encoder = null;

        Picture frame;
        double frameRate = 25.0; // You can set this to match your video's actual FPS
        double duration = endSec - startSec;
        int maxFrames = (int) (duration * frameRate);
        int count = 0;

        while ((frame = grab.getNativeFrame()) != null && count < maxFrames) {
            if (encoder == null) {
                Size size = frame.getSize();
                encoder = new SequenceEncoder(NIOUtils.writableChannel(outputFile), Rational.R((int) frameRate, 1));
            }
            encoder.encodeNativeFrame(frame);
            count++;
        }

        if (encoder != null) {
            encoder.finish();
        }

        inChannel.close();
        System.out.println("Video cut completed: " + outputPath);
    }

    public static void main(String[] args) {
        try {
            cutMp4("input.mp4", "output.mp4", 5.0, 15.0); // Cut from second 5 to 15
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

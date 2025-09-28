# Some tools

The [tools dir](https://github.com/bitplane/undockit/tree/master/tools) contains
some executable Dockerfiles that you can use. These have been pushed to Docker
Hub [here](https://hub.docker.com/u/bitplanenet). Either copy them into your
`$PATH` and execute directly, or install the prebuilt versions like so:

```bash
undockit install docker.io/bitplanenet/whisper
```

## Speech to Text

### `whisper`

Whisper is OpenAI's transformer-based transcription model. Run
`whisper some_file.whatever` and it'll create subtitles in a bunch of formats.
It can also be used to translate as it transcribes. See `--help` for more info.

## Image processing

### `rembg`

This model removes backgrounds from images. Works great on photos of people,
objects, etc. For example, you'd run `rembg i mugshot.jpg pass.png` to create
security pass photos for your org.

### `yolo`

YOLOv8 object detection, segmentation, and classification. Detect objects in
images with `yolo detect predict source=image.jpg`, or try segmentation with
`yolo segment predict source=image.jpg`.

If you're into this sort of thing, Joseph Redmon taught a class on this, and
it's [available on YouTube](https://www.youtube.com/playlist?list=PLjMXczUzEYcHvw5YYSU92WrY8IwhTuq7p).

## Song separation

Splitting music into different tracks. Can be used to remove vocals (like
my "obscure and obnoxious karaoke" playlist on YouTube), or extracting vocals,
beats or other things for remixing.

Also useful as a pre-processing step when transcribing lyrics, voice cloning
and style transfer.

### `spleeter`

Spleeter is Deezer's song separation model. It does the karaoke thing by default

To split out other components like drums, bass, strings etc you'll need to pick
some other model that's been trained to split out different "stems", see the
`--help` for info. You can also train it to split out whatever you like,
providing you have the data.

### `demucs`

Demucs is Facebook's song splitting model. Same as the above but a bit slower
and better quality. Defaults to 4 stems.

"""Test cases for MIDI I/O."""
from pathlib import Path

import muspy

DATA_DIR = Path(__file__).parent / "data" / "abc"


def test_header():
    musics = muspy.read(DATA_DIR / "header.abc")

    assert len(musics) == 1

    music = musics[0]
    assert music.metadata.title == "TEST: Header lines only"
    assert len(music.metadata.creators) == 1
    assert music.metadata.creators[0] == "Composer"
    assert music.metadata.source_filename == "header.abc"
    assert music.metadata.source_format == "abc"

    assert len(music.tempos) == 1
    assert music.tempos[0].time == 0
    assert music.tempos[0].tempo == 115

    assert len(music.key_signatures) == 1
    assert music.key_signatures[0].time == 0
    assert music.key_signatures[0].root == "C"
    assert music.key_signatures[0].mode == "major"

    assert len(music.time_signatures) == 1
    assert music.time_signatures[0].time == 0
    assert music.time_signatures[0].numerator == 3
    assert music.time_signatures[0].denominator == 4

    assert len(music.tracks) == 0


def test_notes():
    music = muspy.read(DATA_DIR / "notes.abc")[0]

    assert len(music.tracks) == 1

    # Answers
    pitches = [60, 62, 64, 65, 67, 69, 71]

    notes = music.tracks[0].notes
    assert len(notes) == 28
    for i, note in enumerate(notes):
        assert note.start == i * music.resolution
        assert note.duration == music.resolution
        octave, pitch_class = divmod(i, 7)
        assert note.pitch == pitches[pitch_class] + 12 * (octave - 1)


def test_durations():
    music = muspy.read(DATA_DIR / "durations.abc")[0]

    # Answers
    durations = (
        [0.125, 0.125, 0.25, 0.5, 0.75, 1, 1.5, 1.75, 2, 3, 3.75, 4]
        + [0.125, 0.25, 0.25, 0.5, 1, 1.5, 2, 3, 3.5, 4, 6, 7.5]
        + [0.125, 0.25, 0.5, 0.5, 1, 2, 3, 4, 6, 7,]
    )

    notes = music.tracks[0].notes
    assert len(notes) == 34
    for note, duration in zip(notes, durations):
        assert note.duration == int(duration * music.resolution)
        assert note.pitch == 69


def test_broken_rhythm():
    music = muspy.read(DATA_DIR / "broken_rhythm.abc")[0]

    # Answers
    durations = [0.75, 0.25, 1.5, 0.5, 0.875, 0.125, 1.875, 0.125]

    notes = music.tracks[0].notes
    assert len(notes) == 8
    for note, duration in zip(notes, durations):
        assert note.duration == int(music.resolution * duration)
        assert note.pitch == 69


def test_beams():
    music = muspy.read(DATA_DIR / "beams.abc")[0]

    # Answers
    pitches = [69, 71, 72, 74]

    notes = music.tracks[0].notes
    assert len(notes) == 15
    for i, note in enumerate(notes):
        assert note.pitch == pitches[i % 4]


def test_tuplets():
    music = muspy.read(DATA_DIR / "tuplets.abc")[0]

    # Answers
    pitches = []
    durations = []
    ratios = [3 / 2, 2 / 3, 3 / 4, 2 / 5, 2 / 6, 2 / 7]
    for n, ratio in zip(range(2, 8), ratios):
        pitches += [69, 71] * (n // 2)
        if n % 2 > 0:
            pitches.append(69)
        durations += [ratio / 2] * n

    for i, note in enumerate(music.tracks[0].notes):
        assert note.pitch == pitches[i]
        assert note.duration == round(music.resolution * durations[i])


def test_ties():
    music = muspy.read(DATA_DIR / "ties_and_slurs.abc")[0]

    # Answers
    durations = [0.25, 0.25] + [0.5] * 8 + [1, 1.5, 3]

    assert len(music.tracks[0].notes) == 13

    for note, duration in zip(music.tracks[0].notes, durations):
        assert note.pitch == 69
        assert note.duration == int(music.resolution * duration)


def test_accidentals():
    music = muspy.read(DATA_DIR / "accidentals.abc")[0]

    # Answers
    pitches = [67, 68, 69, 70, 71]

    for note, pitch in zip(music.tracks[0].notes, pitches):
        assert note.pitch == pitch
        assert note.duration == int(0.5 * music.resolution)


def test_grace_notes():
    music = muspy.read(DATA_DIR / "grace_notes.abc")[0]

    # Answer
    durations = [1.5, 0.5, 0.5, 0.5] * 2

    for note, duration in zip(music.tracks[0].notes, durations):
        assert note.pitch == 69
        assert note.duration == int(music.resolution * duration)


def test_chords():
    music = muspy.read(DATA_DIR / "chords.abc")[0]

    # Answers
    pitches = (
        [60, 64, 67, 72]
        + [60, 67]
        + [60, 64]
        + [62, 65]
        + [62, 65]
        + [64, 67]
        + [65, 69]
        + [69, 74,]
    )

    for note, pitch in zip(music.tracks[0].notes, pitches):
        assert note.pitch == pitch
        assert note.duration == int(0.5 * music.resolution)


def test_keys_and_modes():
    music = muspy.read(DATA_DIR / "keys_and_modes.abc")[0]

    # TODO: Support changing keys in the middle
    return

    # Answers
    modes = (
        ["major", "major", "major"] * 2
        + ["lydian", "ionian", "mixolydian"]
        + ["dorian", "minor", "minor"]
        + ["aeolian", "phrygian", "locrian"]
    )

    for key_signature, mode in zip(music.key_signatures, modes):
        assert key_signature.mode == mode
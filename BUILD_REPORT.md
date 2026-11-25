# TalentForge-AI build report

Environment: Python 3.12, fresh virtualenv, Linux sandbox (3 GB RAM, no access to huggingface.co).

## Result
- All 22 .py files compile.
- All dependencies install (torch 2.15, transformers 5.24, sentence-transformers, spaCy 3.8 + en_core_web_sm, streamlit 1.67, librosa, fer 25.10, tensorflow-cpu, ...).
- Streamlit starts; /_stcore/health returns ok.
- app.py and all 12 pages load headlessly (signed-out) with no exceptions.
- Functional checks passed: DB creation, register + bcrypt hash/verify, resume parse (spaCy) + score (sample resume = 77.4), specificity score, filler-word count and WPM.

## Build problems found (fixed in the attached requirements.txt)
1. `fer` needs TensorFlow but does not install it -> add `tensorflow` (CPU is enough).
2. `fer` imports `moviepy.editor`, removed in moviepy 2.x -> pin `moviepy<2`.
3. `fer` imports `pkg_resources`, removed in setuptools 81+ -> pin `setuptools<81`.
Without these, `import fer` fails and the Emotion page cannot work.

## Not verified here
- Model weights (all-MiniLM-L6-v2, DistilBERT SST-2, whisper-base) could not be downloaded (HuggingFace blocked), so semantic relevance, sentiment, and speech-to-text were not run end to end. Expect them to work on a machine with internet on first run.
- `FER(mtcnn=True)` aborts in this sandbox with an LLVM "option registered more than once" error (TensorFlow 2.21). `FER(mtcnn=False)` works. This may be sandbox/version specific; test on your machine. If it also crashes there, try an older TensorFlow (e.g. 2.15-2.17) or mtcnn=False.
- Not tested: logged-in flows, webcam, microphone, recruiter matching with real data.

## Run
    python -m venv venv && venv\Scripts\activate
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    streamlit run app.py

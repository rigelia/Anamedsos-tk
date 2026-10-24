# Social Media Analytics: Modules 4 to 6

Source: lecture slides, Fakultas Ilmu Komputer, Universitas Indonesia.
Converted to Markdown for LLM use. Slide content is reproduced faithfully; decorative slides (title pages, Q&A, icon credits) are dropped. Anything in `> Note:` blocks is an editor's note, not slide content.

Contents:
- Module 4: Data Storage and Reproducible Pipeline (Part II: Social Media Data Collection)
- Module 5: Social Media Data Quality (Part III: Data Preparation)
- Module 6: Social Media Data Preprocessing (Part III: Data Preparation)

---

# Module 4: Data Storage and Reproducible Pipeline

Part II: Social Media Data Collection

## Expected Learning Outcomes

You should be able to:
1. Select appropriate data formats for storing social media datasets based on structure, size, and intended use.
2. Design an efficient storage strategy for large-scale social media data.
3. Organize datasets and metadata so that data provenance and processing history can be understood.
4. Apply dataset versioning and experiment tracking to maintain reproducibility.
5. Structure a social media analytics project in accordance with reproducible research practices.
6. Explain the relationship between data storage, data provenance, and reproducibility.

## Topics Covered

- Data Formats: JSON, CSV, and Parquet
- Efficient Data Storage
- Object Storage
- Dataset Organization (metadata, versioning)
- Experiment Tracking
- Reproducible Pipelines

## 4.1 Data Formats

### JSON (JavaScript Object Notation)

- A programming-language-independent data format specified in the early 2000s by Douglas Crockford as a simple and lightweight way to send data between a web server and browser.
- A common data format for API responses and semi-structured social media data.

**Characteristics:**

- **Key-value structure.** Example: `"retweet_count": 4`
- **Nested objects.** Example:
  ```json
  "retweeted_states": {
    "text": "Hello World!",
    "in_reply_to_user_id": null
  }
  ```
- **Arrays as values.** Example: `"hashtags": ["Fasilkom", "CSUI"]`
- **Optional fields.** Some tweets may have geolocation data (`"place"`), others may not.
- **Heterogeneous records.** A JSON file may store various record types (e.g., user, product, post), each with a different set of key-value items.
- **Preserves the original API response.** It has no extra tags like XML.

> Note: In the actual Twitter/X API the field is `retweeted_status`, not `retweeted_states`. The slide likely has a typo.

### CSV (Comma-Separated Values)

- A plain-text format for storing tabular data, like spreadsheets or databases.
- **Rows and columns:** each line is one row (record); commas (the delimiter) separate values into columns.
- The first row is usually the header.
- **Quoting:** values are wrapped in quotes so that commas, line breaks, and quotes inside a value do not break the CSV structure.
- **Encoding:** CSV is not tied to a specific character encoding, but it should be, and generally is, used with UTF-8.
- **Missing values:** because columns are homogeneous, a missing value leaves a blank in that column.
- **No nested values:** CSV is inherently flat, so it cannot store nested values.

Example (source: https://www.kaggle.com/datasets/nixie6254/social-media-dataset):

```csv
Area, Category, Day, Month, Platform, Post Type, Timestamp, User, Week, Year
Aceh, Medium, 15, 1, Twitter, Video, 15/01/2023 12:30:00, User123, 3, 2023
```

### JSON vs. CSV

- **JSON preserves structure.**
- **CSV emphasizes tabular simplicity.**

### Parquet

- "Apache Parquet is an open source, column-oriented data file format designed for efficient data storage and retrieval." (Apache Parquet, 2026, https://parquet.apache.org/)
- Characteristics (Databricks, 2026):
  - Free and open-source file format
  - Language agnostic
  - Column-based format
  - Used for analytics (OLAP) use cases
  - Highly efficient data compression and decompression
  - Supports complex data types and advanced nested data structures

**Columnar storage groups values by column. Row storage groups values by record.**

Illustration (Motherduck, 2026): computing `AVG(amount)` over 4 rows × 4 columns (id, region, amount, ts).
- Row storage: the scan touches every field of every row to reach each amount. Reads 16 of 16 values.
- Columnar storage: the engine reads the `amount` column as one contiguous block and skips the rest. Reads 4 of 16 values.
- Same 4 rows, same 16 values; only the order on disk changes. A query touching 1 of 4 columns reads 25% of the bytes.

### Columnar vs. Row Storage (Motherduck, 2026)

| Dimension | Row storage | Columnar storage |
|---|---|---|
| Layout | One record, all fields, then the next record | One field, all rows, then the next field |
| Best for | OLTP: point reads, inserts, updates | OLAP: scans, `GROUP BY`, filters on a few columns |
| I/O for `AVG(amount)` on a 20-column table | Reads every field of every row | Reads `amount` (and any filter columns) |
| I/O for 3 of 50 columns | Reads all 50 fields (100% of row bytes) | Reads roughly 6% of the bytes |
| Compression | 1.5 to 3× typical | 5 to 10× typical, up to 30× on low-cardinality columns |
| Concurrency | 1000s of point queries per node | 10s to 100s of analytical queries per node |
| `SELECT *` of one row | Cheap | Rebuilds the row from many columns |
| Examples | PostgreSQL, MySQL, SQLite | DuckDB, ClickHouse, Snowflake, BigQuery |

### Format Selection

| Situation | Appropriate format |
|---|---|
| Raw API response | JSON |
| Small tabular dataset | CSV |
| Sharing simple data | CSV |
| Large analytical dataset | Parquet |
| Nested API response | JSON |
| Repeated analytical processing | Parquet |

**There is no universally "best" format.**

## 4.2 Efficient Data Storage

- Social media datasets can be large. Example: one month of Reddit submissions + comments can be around 50 GB compressed. Consider the total size from 2005 until now.
- Because of their size, social media datasets are usually compressed (e.g., gzip, Zstandard, or other formats).
- Compression reduces storage requirements, transfer time, and I/O cost.

**Partitioning** helps avoid scanning irrelevant data. Instead of one `tweet.parquet`, organize as:

```
tweets/
  year=2026/
    month=08/
      data.parquet
    month=09/
      data.parquet
```

## 4.3 Object Storage

- "A technology that stores and manages data in an unstructured format called objects." (AWS, 2026)
- Basic model: Object Storage → Bucket → Objects (each with metadata)
- **Bucket:** a container for objects.
- **Object:** a file plus any metadata describing it. Consists of:
  - **Key:** the object's name (e.g., `tweets/post_id_xx.json`)
  - **Value:** the data itself
  - **Metadata:** name-value pairs describing the object (e.g., `content-type: application/json`)
  - **Size:** object size
- **Amazon S3:** an object storage service offering industry-leading scalability, data availability, security, and performance.
- **S3-compatible storage:** MinIO, Cloudflare R2.

**Object storage in a reproducible pipeline:**

```
Social Media API → Collection Script → Raw JSON → S3 Bucket → Processing → Parquet → Analysis
```

## 4.4 Dataset Organization

Recommended folder structure:

```
data/
  raw/        # data exactly as collected
  interim/    # data produced during transformation
  processed/  # data ready for analysis
  external/   # datasets obtained from other sources
```

Data lifecycle:

```
Collection → Raw Data → Cleaning → Intermediate Data → Transformation → Processed Data → Analysis → Results
```

### Metadata Management

Metadata is data about data, and it needs to be managed. Important categories:

- **Dataset metadata:** dataset name, description, creator, creation date, size, number of records.
- **Collection metadata:** platform, API or scraping method, query, collection period, collection script/version.
- **Provenance metadata:** where did the dataset come from? Example chain:
  ```
  dataset_v03.parquet
    ← processed by clean_posts.py v1.4
    ← raw_posts_2026-09-10.json
    ← API collection script v2.1
    ← X API
  ```

### Dataset Versioning

- Datasets change. Example: dataset v1 → remove duplicates → dataset v2 → fix language detection → dataset v3.
- **The original dataset should not be overwritten.**
- Preserve: original/raw data, transformation scripts, dataset versions, processing parameters.
- A version should be identifiable and explainable.

## 4.5 Experiment Tracking

Experiment tracking connects data storage to the reproducibility of analysis.

Example: sentiment analysis run twice, changing only the model.

| | Experiment 1 | Experiment 2 |
|---|---|---|
| Dataset | tweet_v03 | tweet_v03 |
| Model | IndoBERT | XLM-R |
| Learning rate | 2e-5 | 1e-5 |
| Epochs | 5 | 5 |
| Batch size | 16 | 16 |
| Accuracy | 89.2% | 90.1% |

We need to know which experiment produced which result.

> Note: the slide says "we change the model", but the learning rate also changed (2e-5 vs 1e-5). Two variables changed, so the accuracy difference cannot be attributed to the model alone. This is itself a good illustration of why tracking matters.

Experiment tracking should record:
- Dataset version
- Preprocessing version
- Model
- Parameters
- Random seed
- Evaluation metrics
- Execution date
- Code version

## 4.6 Reproducible Pipelines

**Reproducible research:** another researcher should be able to understand and, where data and platform conditions permit, reproduce the computational steps that produced the reported results.

- **Non-reproducible workflow:** Collect data → Manual Excel cleaning → Copy/paste → Notebook → Final graph
- **Reproducible workflow:** Raw Dataset → Processing Script → Processed Dataset → Analysis Script → Experiment Record → Result

### Reproducibility Checklist

Document all of these:
- Data source
- Collection date
- Collection method
- Query/filter
- Preprocessing
- Software/library versions
- Parameters
- Random seeds
- Dataset versions
- Analysis procedures
- Limitations

### Reproducible Social Media Pipeline (diagram)

```
Social Media Platform
  → Data Collection
  → Raw Data
  → Data Validation
  → Data Transformation
  → Processed Data
      ├─ Data Analysis → Experiments ────────┐
      └─ Data Versioning → Dataset Metadata ─┤
                                             → Reproducible Results
```

## References (Module 4)

- https://www.json.org/json-en.html
- https://parquet.apache.org/
- https://www.databricks.com/blog/what-is-parquet
- https://motherduck.com/learn/columnar-storage-guide/
- https://aws.amazon.com/what-is/object-storage/
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html

---

# Module 5: Social Media Data Quality

Part III: Data Preparation

## Topics Covered

- Part 1: Data Quality Foundations
- Part 2: Authenticity, Bots, Spam & Noise
- Part 3: Sampling, API Bias & Network Quality

> Note: In the provided slides, Parts 2 and 3 contain only title slides, and the References slide is empty. Only Part 1 has content.

## Part 1: Data Quality Foundations

### Expected Learning Outcomes

You should be able to:
1. Explain major dimensions of data quality;
2. Identify missing and duplicate data;
3. Distinguish invalid, incomplete, and inconsistent data;
4. Perform basic data validation.

### Can We Trust the Data We Collected?

Pipeline position: Collection → Storage → **Data Quality** → Preprocessing → Analysis

- Having a dataset does not mean we can immediately analyze it.
- What if most of the dataset contains duplicates or bot posts, the time period is too narrow, or some keywords were excluded?
- We need to ask whether the data is good enough to answer our question: is it complete, valid, authentic, and representative enough for the research purpose?

### The Big Data Fallacy

**More data ≠ better data.**

### What Is Data Quality?

- Data quality is the degree to which data is suitable for its intended purpose.
- **Key idea:** quality is context-dependent.
- **Fit for purpose:** a dataset can be adequate for one research question but inadequate for another.

### Completeness

"Do we have the information we need?" Ask:
- Is there missing post text?
- Missing timestamp?
- Missing user ID?
- Missing language?
- Missing engagement?

**Important distinction: zero ≠ missing.** Example: `likes = 0` vs `likes = NULL`.

### Missing Data Example

| ID | Text | Timestamp | Location |
|---|---|---|---|
| 101 | Good! | 10:01 | Jakarta |
| 102 | Great! | (missing) | Jakarta |
| 103 | (missing) | 10:03 | (missing) |

Which records can still be used?

### Five Strategies for Handling Missing Data

**Strategy 1: Remove it**
- Consider removing when:
  - The missing field is essential to the analysis.
  - The record contains too little useful information.
  - The proportion of missing records is small.
  - The missingness makes the record unusable.
  - A predefined quality rule says to exclude it.
- Example: for sentiment analysis, remove posts with no text.
- **Caution:** removing observations can introduce bias. Example: if location is mostly missing for users outside major cities, the dataset may become disproportionately urban.
- **Note:** removing missing data changes the dataset.

**Strategy 2: Retain it**
- Do nothing; keep the missing value.
- Example: location is missing but not required for your research question, so there is no reason to remove the record.
- A missing value in one variable does not necessarily make the entire record useless.

**Strategy 3: Flag it**
- Instead of changing or removing the record, create an indicator column.
- Retains the original data and explicitly documents the problem.
- The missingness itself might carry information.
- Supports reproducibility.

| post_id | location | location_missing |
|---|---|---|
| 101 | Jakarta | FALSE |
| 102 | (missing) | TRUE |
| 103 | Bandung | FALSE |

**Strategy 4: Impute it**
- Estimate the missing value from other information.
- **Caution:** imputation can produce highly questionable results, especially with social media data. Example: imputing missing location as "Jakarta". Why Jakarta?
- Unless there is a defensible methodological reason, do not impute.
- Never confuse an "unknown" value with a meaningful value.

**Strategy 5: Collect the data again**
- Sometimes the best solution. Investigate why data is missing. Possible causes:
  - API request omitted the field
  - Scraper extracted the wrong HTML element
  - API response changed
  - Collection code has a bug
  - Pagination logic failed
- If the problem is in the collection pipeline, preprocessing cannot fix it.

### Two Distinctions to Keep in Mind

- Missing because **the value does not exist** (genuine absence)
- versus missing because **we failed to collect it** (collection problem)

### Decision Tree for Missing Data

```
Missing Value
└─ Why is it missing?
   ├─ Collection problem
   │  └─ Can we retrieve it?
   │     ├─ Yes → Collect again
   │     └─ No  → Flag / Retain
   └─ Genuine absence
      └─ Is the variable necessary?
         ├─ Yes → Remove / Consider imputation
         └─ No  → Retain
```

### Comparing the Five Strategies

| Strategy | What happens? | When useful? | Main risk |
|---|---|---|---|
| Remove | Delete record/value | Essential information is missing | Sampling bias |
| Retain | Keep NULL/missing | Variable isn't essential | Reduced usable data |
| Flag | Keep + mark missingness | Need transparency/investigation | More complex analysis |
| Impute | Estimate value | Defensible estimation is possible | Introduces assumptions |
| Collect again | Retrieve original data | Collection failure caused missingness | May be impossible |

### Missingness Can Be Biased

- **Key point: missing data is not necessarily random.** Example: a user may intentionally not share their location. This can lead to different conclusions.
- **Random missingness:** missingness has little or no relationship to the characteristics being studied.
- **Systematic missingness:** missingness is related to characteristics of the users, posts, or phenomenon.

### Duplicate Data

Possible causes:
- Repeated API requests
- Pagination errors
- Retries
- Dataset merging
- Crawler problems

### Duplicate Data ≠ Repeated Content

- **Exact duplicate:** ID 101 and ID 101 (the same record twice).
- **Repeated content:** User A: "This class is amazing!" and User B: "This class is amazing!" (different records, same text).
- **Legitimate repost:** a user intentionally reposts existing content.
- **Key point:** deduplication requires a definition of what counts as a duplicate.

### Accuracy, Validity & Consistency

| Dimension | Question | Example |
|---|---|---|
| Accuracy | Is it correct? | Wrong location |
| Validity | Does it follow rules? | Negative likes |
| Consistency | Does it agree? | Conflicting timestamps |

### Data Validation

The process of checking whether data meets predefined expectations. Example rules:
- `post_id` is not NULL
- `timestamp` is valid
- text length > 0
- `likes >= 0`
- `post_id` is unique

### Validation at Three Levels

- **Record level:** "Is this record valid?" Examples: NULL ID, invalid timestamp, negative likes.
- **Dataset level:** "Is the dataset internally consistent?" Examples: missing periods, duplicates, unexpected distributions.
- **Research level:** "Is this dataset appropriate for our questions?" Examples: sampling bias, platform bias, missing population groups.

**Key takeaway:** valid records do not automatically make a valid dataset, and a valid dataset does not automatically answer a valid research question.

### Quality Gate

```
Raw Data → Data Quality Assessment → Validated Data → Analysis
```

Assess data quality before performing analysis.

### Part 1 Takeaways

1. Large data is not necessarily good data.
2. Missing and duplicate data can affect results.
3. Data quality should be assessed before analysis.

## Part 2: Authenticity, Bots, Spam & Noise

(No content in provided slides.)

## Part 3: Sampling, API Bias & Network Quality

(No content in provided slides.)

---

# Module 6: Social Media Data Preprocessing

Part III: Data Preparation

## Expected Learning Outcomes (Module)

You should be able to:
1. Explain why social media text requires specialized preprocessing;
2. Apply common text preprocessing techniques to social media data;
3. Handle emojis, hashtags, URLs, mentions, slang, and code-mixing;
4. Explain the trade-offs between aggressive cleaning and information preservation;
5. Design a preprocessing pipeline appropriate for an analytical task;
6. Split datasets into training, validation, and test sets without data leakage.

## Topics Covered

- Part 1: From Raw Text to Clean Text
- Part 2: Social Media & Indonesian NLP
- Part 3: Building a Task-Specific Pipeline

## Part 1: From Raw Text to Clean Text

Guiding question: what should we remove, and what should we preserve?

### Expected Learning Outcomes

You should be able to:
1. Identify common sources of noise in social media text;
2. Perform basic text cleaning and tokenization;
3. Explain the purpose and risks of stopword removal;
4. Distinguish stemming from lemmatization;
5. Make preprocessing decisions based on the downstream task.

### Why Is Social Media Text Difficult?

Example post:

> @user GILAAA 😭😭 this movie is sooo GOOD!!! https://t.co/abc #MovieNight

It contains:
- Repeated punctuation and characters
- URLs and mentions
- Emojis
- Informal spelling and slang
- Hashtags
- Mixed capitalization

### Key Principle: Noise Is Task-Dependent

| Element | Sentiment | Topic modeling |
|---|---|---|
| 😭 | Potentially important | Potentially useful |
| `!!!` | Potentially useful | Usually less useful |
| `@netflix` | Usually replace/remove | Usually replace/remove |
| `#MovieNight` | Potentially useful | Potentially useful |
| URL | Usually replace/remove | Usually replace/remove |
| `sooo` | May express intensity | May need normalization |

### Text Cleaning

- Unicode and character normalization
- Whitespace normalization
- Handling unwanted control characters
- Punctuation handling
- Case normalization
- **Do not automatically remove unusual elements: they may carry meaning.**

### Example: Cleaning Can Remove Information

- Raw: `OMG!!!  This   is AMAZING!!! 😍😍`
- Cleaned: `omg this is amazing 😍😍`

What changed?
- Capitalization (lost)
- Repeated punctuation (lost)
- Whitespace (normalized)
- Emoji information is preserved

### Tokenization

Example: `I love Indonesian food!` → `["I", "love", "Indonesian", "food", "!"]`

Types:
- Word tokenization
- Subword tokenization
- Character tokenization

### Traditional NLP vs. Transformer NLP

| Traditional NLP | Transformer NLP |
|---|---|
| Sentence → words → features | Sentence → subword tokens → embeddings → model |
| Often uses TF-IDF / bag-of-words | Uses contextual representations |
| Tokenization is often explicit | Tokenizer is part of the model pipeline |

TF-IDF (Term Frequency-Inverse Document Frequency): a statistical score measuring how important a word is to a document within a larger collection of documents.

### Stopword Removal

- Stopwords are frequent words that may contribute little to some analyses.
- English examples: the, is, and, of, to
- Indonesian examples: yang, dan, di, ke, dari, untuk (source: https://github.com/stopwords-iso/stopwords-id)
- Useful in some traditional NLP pipelines, but not universally.

### The Stopword Problem

```
"I do not like this"  → stopword removal →  "like"
```

Negation may be critical for sentiment. Removing stopwords can flip or erase polarity.

### Stemming vs. Lemmatization

| Technique | Idea | Example |
|---|---|---|
| Stemming | Reduce using rules | playing → play |
| Lemmatization | Reduce to linguistic base form | better → good |
| Indonesian stemming | Reduce morphological variants | berlari → lari |

Trade-off: vocabulary consistency vs. preservation of morphological information.

### Mini Exercise: Three Preprocessing Versions

Input post:

> @user Aku GAKKK suka film ini 😭😭😭!!! #FilmIndonesia https://...

Produce three versions:
- **A. Minimal cleaning:** preserve as much information as possible.
- **B. Traditional NLP:** clean more aggressively for TF-IDF/topic modeling.
- **C. Transformer input:** preserve much of the original linguistic information.

For each version, justify what you removed, replaced, or preserved.

## Part 2: Social Media & Indonesian NLP

Social media language is not textbook language.

### Expected Learning Outcomes

You should be able to:
1. Process emojis, hashtags, URLs, and mentions;
2. Normalize informal social media language;
3. Explain slang normalization;
4. Identify code-mixing;
5. Describe challenges in Indonesian NLP;
6. Design preprocessing rules that preserve relevant information.

### Emoji Processing

Post: `I love this 😍🔥`

| Strategy | Representation |
|---|---|
| Remove | `I love this` |
| Keep | `I love this 😍🔥` |
| Convert | `I love this smiling_face_with_heart_eyes fire` |

### Hashtag Processing

| Strategy | Example |
|---|---|
| Keep | `#IndonesianFood` |
| Remove `#` | `IndonesianFood` |
| Segment | `Indonesian Food` |

Hashtag segmentation can preserve useful topic information, but it is not always perfect.

### URL and Mention Processing

| Raw | Possible representation |
|---|---|
| `https://example.com/article` | `[URL]` |
| `@Netflix this show is amazing` | `[USER] this show is amazing` |

Replacing preserves the fact that a URL or mention occurred without retaining the specific identifier.

### Slang Normalization

| Social media | Normalized |
|---|---|
| gak / ga / nggak | tidak |
| kalo | kalau |
| yg | yang |
| bgt | banget |
| aja | saja |

### But Normalization Can Lose Expression

`baguuuusss` → normalized into → `bagus`

Vocabulary consistency improves, but expressive intensity may be lost.

### Indonesian NLP Challenges

- Informal morphology: nge-like, di-like, ngelike
- Affixation: makan, memakan, dimakan, makanan
- Informal spelling: bgt, bangettt
- Regional and informal vocabulary
- Multiple languages in the same dataset
- Platform-specific expressions and slang

### Code-Mixing

Example: `Aku lagi prepare buat presentation besok.`

- Indonesian + English in the same utterance.
- An Indonesian-only pipeline may mishandle English words.
- Normalization can incorrectly transform words from another language.
- Language identification may be needed at sentence or token level.

### Text Normalization Pipeline

```
Raw Text
→ Unicode/Character Normalization
→ URL & Mention Handling
→ Emoji Processing
→ Hashtag Processing
→ Slang Normalization
→ Code-Mixing Handling
→ Tokenization
```

The order is not universal; it depends on what each operation needs as input.

## Part 3: Building a Task-Specific Pipeline

Preprocessing is part of the experiment.

### Expected Learning Outcomes

You should be able to:
1. Construct an end-to-end preprocessing pipeline;
2. Choose preprocessing operations based on an analytical task;
3. Compare alternative preprocessing strategies;
4. Explain preprocessing as an experimental decision;
5. Correctly split data into training, validation, and test sets;
6. Identify basic forms of data leakage.

### From Techniques to Pipeline

```
Raw Text
→ Unicode/Character Normalization
→ URL & Mention Handling
→ Emoji Processing
→ Hashtag Processing
→ Slang Normalization
→ Code-Mixing Handling
→ Tokenization
→ Model-Ready Text
```

### Task-Specific Preprocessing

| Sentiment analysis | Topic modeling | Transformer classification |
|---|---|---|
| Preserve negation | Stopword removal may help | Preserve contextual information |
| Preserve emojis | Vocabulary filtering | Use model tokenizer |
| Preserve intensifiers | Stemming/lemmatization may help | Avoid unnecessary cleaning |
| Be cautious with stemming | Hashtag processing | Preserve word order/context |

### Sentiment Analysis: What to Preserve?

- Negation: not, tidak, jangan
- Emojis and expressive punctuation
- Intensifiers: very, banget, sooo
- Sentiment-bearing hashtags
- Informal expressions that carry affect
- Avoid transformations that erase polarity or intensity

### Topic Modeling: What May Help?

- Stopword removal can reduce common-word dominance.
- Stemming or lemmatization can reduce vocabulary fragmentation.
- Hashtag processing can expose topic-bearing words.
- Vocabulary filtering can remove extremely rare or frequent terms.
- Human interpretability remains important when evaluating topics.

### Transformer-Based Classification

- Transformers use contextual representations.
- Much of the original linguistic structure can be useful.
- Avoid assuming traditional preprocessing is required.
- Use the tokenizer associated with the model.
- Compare preprocessing choices empirically when they matter to the research question.

### Preprocessing as an Experiment Variable

| Pipeline A | Pipeline B | Pipeline C |
|---|---|---|
| Minimal cleaning | Cleaning + slang normalization | Cleaning + slang normalization + stemming |
| Baseline | Normalized text | More aggressive normalization |

Compare downstream performance rather than assuming one pipeline is universally best.

### How Do We Evaluate the Effect?

- Classification: accuracy, precision, recall, F1-score.
- Topic modeling: topic coherence, topic diversity, human interpretability.
- Document preprocessing decisions and configurations.
- Treat preprocessing as part of the experimental design.

### Data Splitting

Determines how we train, tune, and evaluate a model.
- **Training data:** used to learn the model's parameters.
- **Validation data:** used to make decisions about the model.
- **Test data:** used for the final evaluation.

Common techniques:
- 70/15/15, 80/10/10, 80/20 splits
- K-fold cross-validation

### Data Leakage

Example: `"Great product! I love it."` appears in both training and test sets → data leakage.

- Train/test duplicates can make evaluation unrealistically easy.
- Near-duplicate posts may appear in both sets.
- Retweets or reposts can cross dataset boundaries.
- Preprocessing steps that learn from data should be fitted only on training data when appropriate.
- Author leakage can occur when the same users appear in both train and test.

### Random Splitting Is Not Always Enough

| Research goal | Possible split |
|---|---|
| General random classification | Random train/validation/test |
| Predict future posts | Temporal split |
| Generalize across users | User-level split |

How you split the data defines what "generalization" means.

### Final Activity: Design a Pipeline

Example research question: "What factors influence sentiment toward Indonesian AI tools?"

| Stage | Decision | Justification |
|---|---|---|
| URL | Replace with `[URL]` | Preserve URL presence |
| Mention | Replace with `[USER]` | Avoid user-specific vocabulary |
| Emoji | Preserve | Potential sentiment information |
| Hashtag | Segment | Preserve topic information |
| Slang | Normalize | Reduce vocabulary variation |
| Stopwords | Do not remove | Preserve contextual information |

### Discussion: What Could Change the Results?

- Which preprocessing choices could change the research findings?
- Which information might be lost?
- Which transformations could introduce bias?
- Would the same pipeline be appropriate for sentiment analysis and topic modeling?
- What preprocessing decisions should be reported in the paper?

### Final Takeaway

**There is no universally correct preprocessing pipeline.** The appropriate pipeline depends on:
- the data;
- the research question;
- the text representation and model;
- what information should be preserved.

Preprocessing choices should be explicit, reproducible, and justified.

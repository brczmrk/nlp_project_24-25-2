# One-Pager Report

Project by Baricz Márk Róbert (HPKVOW).

## Approaches / Ideas

This project was pretty new territory for me, so it took a while to get comfortable with the practical side and to turn my theoretical knowledge into working code.

### BLIP

My first attempt was using BLIP for image captioning. Unfortunately, it didn’t work out as I hoped—the captions were usually under 10 words, which wasn’t enough. I tried tweaking different parameters, but couldn’t get the results I needed.

### LLaVa

After digging through the slides and doing some research online, I decided to try LLaVa. I was optimistic and planned out a pipeline:

- Generate image descriptions (LLaVa)
- Detect text in images (TrOCR)
- Add detected text to descriptions (LLM)
- Batch descriptions and generate a structured report (LLM)
- Iterate and update the report as needed
- Clean up the final report (LLM)

I got through the first two steps, but ran into issues. The descriptions were better, but still not specific or unique enough—I couldn’t reliably identify the brand or model in the images. On top of that, inference was slow: about 2 minutes per image, and with up to 70 images per object, that just wasn’t practical. With these roadblocks, I started looking for another solution.

### GPT

GPT was actually one of my first ideas, but I thought other models might be better. Since we got access to OpenAI models through Raiffeisen, I figured there must be a reason, so I gave GPT a shot. It supports image captioning and, to my surprise, the results were much better than expected. The descriptions even included text from the images, so the pipeline became a lot simpler.

I tested three models (gpt-4o, gpt-4.1-mini, gpt-4.1) and, after checking OpenAI’s docs for quality and pricing, I settled on GPT-4.1 mini—it’s high quality and much cheaper than the full-size model. I also experimented with different prompts for both description and aggregation tasks. I found that batching didn’t make a big difference for my dataset size, but for much larger datasets (thousands of images), batching would be necessary for performance.

## Other Difficulties

While working on these approaches, I used Jupyter notebooks, but the project needed an API, so I had to learn Flask and spend some time debugging. Docker was also a requirement, which was new to me, but after some trial and error, I managed to set up a basic container.

## Future Improvements

### Batching

As mentioned, batching will be important for larger datasets to keep performance reasonable, since fewer descriptions per batch help the attention layers work better.

### Separate Report Generation

Splitting the report generation into separate requests for each heading could improve performance, since prompts could be more focused and fewer tokens would be needed.

## Conclusion

I found the project topic interesting and started coding with a lot of enthusiasm, but quickly realized it was pretty challenging—especially for beginners like me.

There were plenty of difficulties, but the biggest issue was hardware. Good hardware is essential in this field, but it’s either not free or only available for a limited time (like Colab’s free plan), which makes things tough.

Overall, this project and the course got me more interested in Natural Language Processing. I feel like I need more knowledge and especially more hands-on experience, which I am hoping to get in the future.

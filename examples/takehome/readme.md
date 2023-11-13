# Notion Takehome Assessment

## Description
Given a CSV file of book ratings, this program generates a Notion table with the aggregated ratings for each book title. Book titles are normalized to remove variations due to spacing and capitalization. The average rating for each book and the number of favorite (5-star)  ratings it received are recorded.

To run this program, use Python as follows:
    
    python takehome.py

## Short Answers
> Was there anything you got stuck on, and if so what did you do to resolve it?

I initially hit a roadblock when learning to use the Notion API. In particular, the syntax for properties was confusing to me at first. To resolve this, I found additional resources on the Notion API online and studied their code. In doing so, I successfully overcame this hurdle and grew my understanding of the API.

> Do you have any suggestions for improving the API documentation to make it clearer or easier to use?

I was well-pleased by the clean UI and usability of the API documentation. As a suggestion, I believe additional examples in the documentation itself would be helpful--though there were a wide variety of examples in the example projects, it was sometimes difficult to find corresponding examples in the example projects.

## Major Sources
- [Notion Python API Documentation](https://github.com/ramnes/notion-sdk-py) and [examples](https://github.com/ramnes/notion-sdk-py/tree/main/examples)
- Pandas Documentation, in particular, "[Group by](https://pandas.pydata.org/docs/user_guide/groupby.html)"
- [StackOverflow response on properties](https://stackoverflow.com/questions/75940543/notion-api-filter-query-construction)

## Libraries Used
- [Pandas](https://pandas.pydata.org/) for data processing
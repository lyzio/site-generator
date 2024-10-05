import os
import markdown
import yaml
from jinja2 import Environment, FileSystemLoader
from bs4 import BeautifulSoup
import datetime
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree

# Initialize the Jinja2 environment with the correct loader
env = Environment(loader=FileSystemLoader('_includes'))

def render_template(template_name, context):
    template = env.get_template(template_name)
    return template.render(context)

# Define the paths
pages_dir = '_pages'
posts_dir = '_posts'
output_dir = 'output'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Process each markdown file in the _pages directory
for filename in os.listdir(pages_dir):
    if filename.endswith('.md'):
        filepath = os.path.join(pages_dir, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split the content into metadata and markdown
        parts = content.split('---')
        metadata = yaml.safe_load(parts[1]) if len(parts) > 1 else {}
        markdown_content = ''.join(parts[2:]) if len(parts) > 2 else ''
        
        # Convert markdown to HTML
        html_content = markdown.markdown(markdown_content)
        
        # Render the HTML using the template
        rendered_html = render_template('page_template.html', {
            'metadata': metadata,
            'content': html_content
        })
        
        # Write the rendered HTML to the output directory
        output_filename = os.path.splitext(filename)[0] + '.html'
        output_filepath = os.path.join(output_dir, output_filename)
        
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(rendered_html)

print("HTML generation of pages complete.")

# Process each markdown file in the _posts directory
posts = []
for filename in os.listdir(posts_dir):
    if filename.endswith('.md'):
        filepath = os.path.join(posts_dir, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split the content into metadata and markdown
        parts = content.split('---')
        metadata = yaml.safe_load(parts[1])
        markdown_content = ''.join(parts[2:])
        
        # Convert markdown to HTML
        html_content = markdown.markdown(markdown_content)
        
        # Render the HTML using the template
        rendered_html = render_template('post_template.html', {
            'metadata': metadata,
            'content': html_content
        })
        
        # Write the rendered HTML to the output directory
        output_filename = os.path.splitext(filename)[0] + '.html'
        output_filepath = os.path.join(output_dir, output_filename)
        
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        
        # Collect post metadata and content for the index
        posts.append({'metadata': metadata, 'url': output_filename, 'content': html_content})

print("HTML generation of posts complete.")

# Render the index page
index_html = render_template('index_template.html', {
    'title': 'Blog Index',
    'posts': posts
})

# Write the index HTML to the output directory
with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_html)

print("Index generation complete.")

# Copy the style.css from the _includes directory to the output directory
css_src = os.path.join('_includes', 'style.css')
css_dst = os.path.join(output_dir, 'style.css')

if os.path.exists(css_src):
    with open(css_src, 'r', encoding='utf-8') as src_file:
        css_content = src_file.read()
    
    with open(css_dst, 'w', encoding='utf-8') as dst_file:
        dst_file.write(css_content)

print("CSS file copied to output directory.")
# Copy the style.css from the _includes directory to the output directory
css_src = os.path.join('_includes', 'style.css')
css_dst = os.path.join(output_dir, 'style.css')

if os.path.exists(css_src):
    with open(css_src, 'r', encoding='utf-8') as src_file:
        css_content = src_file.read()
    
    with open(css_dst, 'w', encoding='utf-8') as dst_file:
        dst_file.write(css_content)

print("CSS file copied to output directory.")


# Function to create RSS feed
def create_rss(posts, output_dir):
    rss = Element('rss', version='2.0')
    channel = SubElement(rss, 'channel')
    
    title = SubElement(channel, 'title')
    title.text = 'Blog RSS Feed'
    
    link = SubElement(channel, 'link')
    link.text = 'http://margherita.se'
    
    description = SubElement(channel, 'description')
    description.text = 'Latest blog posts'
    
    # Add atom:link with rel="self"
    atom_link = SubElement(channel, 'atom:link', href='http://margherita.se/rss.xml', rel='self', type='application/rss+xml')
    atom_link.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
    
    for post in posts:
        item = SubElement(channel, 'item')
        
        title = SubElement(item, 'title')
        title.text = post['metadata'].get('title', 'No title')
        
        link = SubElement(item, 'link')
        link.text = f"http://margherita.se/{post['url']}"
        
        description = SubElement(item, 'description')
        description.text = post['content']
        
        pub_date = SubElement(item, 'pubDate')
        pub_date.text = post['metadata'].get('date', datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z'))
        
        # Add guid element
        guid = SubElement(item, 'guid')
        guid.text = f"http://margherita.se/{post['url']}"
        guid.set('isPermaLink', 'true')
    
    rss_tree = ElementTree(rss)
    rss_tree.write(os.path.join(output_dir, 'rss.xml'), encoding='utf-8', xml_declaration=True)

# Generate RSS feed
create_rss(posts, output_dir)

print("RSS feed generation complete.")
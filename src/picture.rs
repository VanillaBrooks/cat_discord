use std::collections::HashSet;

use std::fs;
use std::io::prelude::*;

use super::error;
use super::files;
pub fn find_picture(
    previous: &mut HashSet<String>,
    api: &files::Api,
) -> Result<String, error::Error> {
    // dbg! {"getting posts"};
    let posts = api.get_sub("https://old.reddit.com/r/cats/.json")?;
    // dbg! {"got posts"};
    let mut link_posts = posts
        .into_iter()
        .filter(|x| x.is_valid() && !previous.contains(x.id()))
        .collect::<Vec<_>>();

    link_posts.sort_unstable_by(|left, right| {
        let lu = left.upvotes();
        let ru = right.upvotes();

        if lu > ru {
            std::cmp::Ordering::Less
        } else if ru > lu {
            std::cmp::Ordering::Greater
        } else {
            std::cmp::Ordering::Equal
        }
    });

    // dbg! {&link_posts};
    for _ in 0..link_posts.len() {
        let post = link_posts.remove(0);

        // dbg! {&post};

        if let Ok(file_name) = download_post(&post, &api) {
            previous.insert(post.id_own());
            return Ok(file_name);
        } else {
            continue;
        }
    }

    Err(error::Error::Picture(error::PictureError::NoValidPictures))
}

fn download_post(post: &files::Post, api: &files::Api) -> Result<String, error::PictureError> {
    // dbg! {"downloading picture"};
    let mut res = api.download_picture(post.url())?;

    // dbg! {"got response"};

    #[allow(unused_must_use)]
    match fs::create_dir("temp") {_=>()}

    let _path = format! {"temp/{}.png", post.id()};
    let path = std::path::Path::new(&_path);
    let mut file = fs::File::create(path)?;

    // dbg! {&_path};

    let mut buffer = Vec::with_capacity(10_000);
    res.read_to_end(&mut buffer)?;

    file.write_all(&buffer)?;

    Ok(_path)
}

pub fn get_previous_pictures() -> HashSet<String> {
    match _get_previous_pictures() {
        Ok(set) => set,
        Err(_) => HashSet::new(),
    }
}

fn _get_previous_pictures() -> Result<HashSet<String>, std::io::Error> {
    let path = std::path::Path::new("temp/");
    let dir = path.read_dir()?;

    let names = dir
        .filter(|dir_entry| dir_entry.is_ok())
        .map(|dir_entry| dir_entry.unwrap().file_name().into_string())
        .filter(|file_name| file_name.is_ok())
        .map(|file_name| {
            // get only the data without the extension
            file_name
                .unwrap()
                .split('.')
                .collect::<Vec<&str>>()
                .remove(0)
                .to_string()
        })
        .collect::<HashSet<_>>();

    Ok(names)
}

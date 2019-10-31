mod discord;
mod error;
mod files;
mod picture;

fn main() {
    let api = files::Api::new();
    let prev = picture::get_previous_pictures();
    let x = discord::start_bot(prev, api);

    dbg! {&x};
}

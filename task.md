修改推特抓取逻辑。

目前存在的问题时抓取到的文章段落错误，原始html没有正确的<p>标签区分段落，应该是使用css样式在页面上进行分段处理的。所以我们抓取到的markdown文章所有的内容都是不分段，挤在一起。现在你需要找到规律，把原本没有分段的html标签，在合适的位置加上<p>标签，替换原来的html。这样传到后续的处理流程就能正确转换markdown了。我猜测规律应该藏在`data-offset-key`这个标签中

原则：

- 本次改动不涉及http请求，我已经把html文件保存到本地，在根目录下的`debug1.html`，你可以使用`uv run mdcli debug1.html`进行调试
- 不需要使用`scripts`目录下的任何脚本，这些都是请求网络的
- 只需要改动`src/omni_article_markdown/extractors/twitter.py`一个文件
- 下面是一段正确转换后的示例，你观察一下应该分段的地方：

```
Vue developers have wanted native for years. The ["Vue + Lynx = Vue Native"](https://x.com/danielkelly_io/status/1899746975588737407) tweet pulled 1.7k likes. The [Vue integration issue](https://github.com/lynx-family/lynx/issues/193) on our repo hit 1,600 upvotes -- our biggest feature request ever. The demand was clear; the question was bandwidth.

When [Lynx](https://lynxjs.org/) open-sourced a year ago, [Evan You](https://x.com/youyuxi/status/1898663514581168173) and [Rich Harris](https://x.com/Huxpro/status/1927276405328429259) both shouted it out, but production-quality framework integration has always demanded serious engineering bandwidth. Then projects like [Vercel's web streams rewrite](https://vercel.com/blog/we-ralph-wiggumed-webstreams-to-make-them-10x-faster) and [Cloudflare's ViNext](https://blog.cloudflare.com/vinext/) showed how solo engineers, armed with AI, can ship what used to take a team. That changed the math for me.

Vue already has the foundation: a mature Custom Renderer API. I spent a weekend on it. One ~$1,400, 37-hour hackathon. It started with a design exploration: "Can Vue's Custom Renderer even work with dual-thread code splitting, and how?" By 3am Sunday I was debugging "Tap to increment doesn't work" with Claude. By Monday morning, I had [a working TodoMVC](https://x.com/Huxpro/status/2028672358912086524). I couldn't resist dropping a subtle subtweet, and it immediately took off on X.
```

```
And beyond Vue core, there's a massive Vue ecosystem waiting for us to adapt and grow on native.

The vision is simple: Vue developers should be able to ship native apps as naturally as they ship for the web today. We're not there yet, but the foundation is in place, and the path is clear.

If you've read this far: [try it](https://vue.lynxjs.org).

Build something. Tell us what's missing.

Oh, and Btw:
```
